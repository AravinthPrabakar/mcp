"""
Copyright (c) 2026, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""

import json
from base64 import b64decode
from contextlib import closing
from gzip import compress
from io import BytesIO
from unittest.mock import MagicMock

import oci
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from oci._vendor.requests import Response
from oracle.oci_object_storage_mcp_server import server
from urllib3.response import HTTPResponse


@pytest.fixture
def sdk_client():
    # Mock only credentials; no key file, OCI profile, or live service is used.
    signer = MagicMock(spec=oci.auth.signers.SecurityTokenSigner)
    return oci.object_storage.ObjectStorageClient(
        {"region": "us-phoenix-1"},
        signer=signer,
        retry_strategy=oci.retry.NoneRetryStrategy(),
    )


@pytest.fixture
def sdk_response(sdk_client, monkeypatch):
    """Fake HTTP transport, retaining real OCI stream handling and MCP serialization."""

    def configure(payload=b"hello", headers=None):
        response = Response()
        response.status_code = 200
        response.headers.update(headers if headers is not None else {"content-type": "text/plain"})
        response.headers["opc-request-id"] = "example-request-id"
        # The stream is independently sized so tests can exercise inaccurate size headers.
        response.raw = HTTPResponse(
            body=BytesIO(payload),
            headers={"content-encoding": response.headers.get("content-encoding", "identity")},
            preload_content=False,
            decode_content=False,
        )
        response.close = MagicMock(wraps=response.close)

        namespace_response = Response()
        namespace_response.status_code = 200
        namespace_response.headers["content-type"] = "application/json"
        namespace_response._content = b'"test_namespace"'
        transport = MagicMock(side_effect=[namespace_response, response])
        monkeypatch.setattr(sdk_client.base_client.session, "request", transport)
        monkeypatch.setattr(server, "get_object_storage_client", lambda: sdk_client)
        return response, transport

    return configure


def test_sdk_get_object_returns_stream_body(sdk_client, sdk_response, monkeypatch):
    object_response, _ = sdk_response(headers={"content-length": "5"})
    transport = MagicMock(return_value=object_response)
    monkeypatch.setattr(sdk_client.base_client.session, "request", transport)

    response = sdk_client.get_object("test_namespace", "test_bucket", "object.txt")

    with closing(response.data):
        assert transport.call_args.kwargs["stream"] is True
        assert response.data is object_response
        assert response.headers["content-length"] == "5"
        assert response.data.raw.read() == b"hello"


async def _get_object(**arguments):
    async with Client(server.mcp) as client:
        return await client.call_tool(
            "get_object",
            {
                "bucket_name": "test_bucket",
                "compartment_id": "test_compartment",
                "object_name": "object.txt",
                **arguments,
            },
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("version_id", [None, "example-version"])
async def test_get_object_accepts_sdk_stream_response(sdk_response, version_id):
    object_response, transport = sdk_response(
        headers={
            "Content-Type": "text/plain; charset=UTF-8",
            "Content-Length": "5",
            "ETag": "example-etag",
            "Version-Id": "example-version",
            "Content-MD5": "XUFAKrxLKna5cZ2REBfFkg==",
            "Last-Modified": "Tue, 17 Nov 2026 14:09:37 GMT",
            "Storage-Tier": "Standard",
            "Opc-Meta-Project": "example-project",
        }
    )
    response = await _get_object(**({"version_id": version_id} if version_id is not None else {}))
    result = response.structured_content

    assert result == {
        "namespace": "test_namespace",
        "bucket_name": "test_bucket",
        "name": "object.txt",
        "size": 5,
        "content": "hello",
        "encoding": "utf-8",
        "etag": "example-etag",
        "md5": "XUFAKrxLKna5cZ2REBfFkg==",
        "time_modified": "2026-11-17T14:09:37Z",
        "storage_tier": "Standard",
        "version_id": "example-version",
        "content_type": "text/plain; charset=UTF-8",
        "content_encoding": None,
        "metadata": {"project": "example-project"},
    }
    assert json.loads(response.content[0].text) == result
    assert transport.call_args.kwargs["stream"] is True
    assert dict(transport.call_args.kwargs["params"])["versionId"] == (version_id or "")
    object_response.close.assert_called_once_with()
    assert object_response.raw.closed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,content_type,encoding",
    [
        ("café ☃".encode(), "text/plain; charset=UTF-8", "utf-8"),
        (b"name,value\nexample,1\n", "text/csv", "utf-8"),
        (b'{"ok":true}', "application/json", "utf-8"),
        (b'{"ok":true}', "application/problem+json", "utf-8"),
        (b"<example/>", "application/xml", "utf-8"),
        (b"<example/>", "application/example+xml", "utf-8"),
        (b"hello", "text/plain; charset=us-ascii", "utf-8"),
        (b"ASCII binary bytes", "application/octet-stream", "base64"),
        (bytes(range(256)), "application/octet-stream", "base64"),
        (b"%PDF-1.7", "application/pdf", "base64"),
        (b"hello", None, "base64"),
        (b"hello", "invalid-content-type", "base64"),
        (b"caf\xe9", "text/plain; charset=iso-8859-1", "base64"),
        (b"hello", "text/plain; charset=unknown-charset", "base64"),
        (b"\xff\xfe", "text/plain; charset=UTF-8", "base64"),
        ("café".encode(), "text/plain; charset=ascii", "base64"),
        (b"", "text/plain", "utf-8"),
        (b"", "application/octet-stream", "base64"),
    ],
)
async def test_get_object_content_is_lossless(sdk_response, payload, content_type, encoding):
    headers = {"content-type": content_type} if content_type is not None else {}
    object_response, _ = sdk_response(payload, headers)

    result = (await _get_object()).structured_content

    assert result["encoding"] == encoding
    assert result["size"] == len(payload)
    restored = (
        result["content"].encode("utf-8")
        if encoding == "utf-8"
        else b64decode(result["content"], validate=True)
    )
    assert restored == payload
    assert result["etag"] is None
    assert result["md5"] is None
    assert result["time_modified"] is None
    assert result["version_id"] is None
    assert result["metadata"] == {}
    object_response.close.assert_called_once_with()
    assert object_response.raw.closed


@pytest.mark.asyncio
async def test_get_object_preserves_compressed_bytes(sdk_response):
    payload = compress(b"a" * 100_000, mtime=0)
    object_response, _ = sdk_response(payload, {"content-type": "text/plain", "content-encoding": "gzip"})
    reader = MagicMock(wraps=object_response.raw.read)
    object_response.raw.read = reader

    result = (await _get_object()).structured_content

    assert result["encoding"] == "base64"
    assert result["content_encoding"] == "gzip"
    assert result["size"] == len(payload)
    assert b64decode(result["content"], validate=True) == payload
    assert all(call.kwargs["decode_content"] is False for call in reader.call_args_list)
    object_response.close.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("length", [server._MAX_GET_OBJECT_BYTES - 1, server._MAX_GET_OBJECT_BYTES])
async def test_get_object_accepts_up_to_byte_limit(sdk_response, length):
    sdk_response(b"a" * length)

    result = (await _get_object()).structured_content

    assert result["size"] == length
    assert result["content"] == "a" * length


@pytest.mark.asyncio
@pytest.mark.parametrize("content_length", [None, "0", "1", "1048576", "999999999", "invalid"])
async def test_get_object_rejects_oversize_regardless_of_size_header(sdk_response, content_length):
    headers = {"content-type": "text/plain"}
    if content_length is not None:
        headers["content-length"] = content_length
    object_response, _ = sdk_response(b"a" * (server._MAX_GET_OBJECT_BYTES + 100), headers)
    reader = MagicMock(wraps=object_response.raw.read)
    object_response.raw.read = reader

    with pytest.raises(
        ToolError, match="exceeds the get_object limit of 1048576 bytes; no content was returned"
    ):
        await _get_object()

    assert sum(call.args[0] for call in reader.call_args_list) == server._MAX_GET_OBJECT_BYTES + 1
    object_response.close.assert_called_once_with()
    assert object_response.raw.closed


@pytest.mark.asyncio
async def test_get_object_reports_actual_size_instead_of_header(sdk_response):
    sdk_response(headers={"content-type": "text/plain", "content-length": "999999999"})

    result = (await _get_object()).structured_content

    assert result["size"] == 5
    assert result["content"] == "hello"


@pytest.mark.asyncio
async def test_get_object_decodes_text_after_joining_chunks(sdk_response, monkeypatch):
    monkeypatch.setattr(server, "_GET_OBJECT_CHUNK_BYTES", 2)
    payload = "a€☃".encode()
    sdk_response(payload)

    result = (await _get_object()).structured_content

    assert result["encoding"] == "utf-8"
    assert result["content"].encode("utf-8") == payload


@pytest.mark.asyncio
@pytest.mark.parametrize("successful_reads", [0, 1])
async def test_get_object_closes_stream_after_read_error(sdk_response, monkeypatch, successful_reads):
    monkeypatch.setattr(server, "_GET_OBJECT_CHUNK_BYTES", 2)
    object_response, _ = sdk_response()
    object_response.raw.read = MagicMock(
        side_effect=[b"he"] * successful_reads + [OSError("simulated stream failure")]
    )

    with pytest.raises(ToolError, match="simulated stream failure"):
        await _get_object()

    object_response.close.assert_called_once_with()
    assert object_response.raw.closed


@pytest.mark.asyncio
async def test_get_object_closes_stream_after_metadata_error(sdk_response):
    object_response, _ = sdk_response(headers={"last-modified": "invalid-timestamp"})

    with pytest.raises(ToolError, match="Invalid date value or format"):
        await _get_object()

    object_response.close.assert_called_once_with()
    assert object_response.raw.closed


@pytest.mark.asyncio
async def test_get_object_advertises_content_response_schema():
    async with Client(server.mcp) as client:
        tool = next(tool for tool in await client.list_tools() if tool.name == "get_object")

    schema = tool.output_schema
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"namespace", "bucket_name", "name", "size", "content", "encoding"}
    assert schema["properties"]["encoding"]["enum"] == ["utf-8", "base64"]
    assert schema["properties"]["size"]["minimum"] == 0
    assert "1048576" in tool.description
