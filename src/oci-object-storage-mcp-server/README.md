# OCI Object Storage MCP Server

## Overview

This server provides tools to interact with the OCI Object Storage resources.
It includes tools to help with managing object storage configurations.

## Running the server

### STDIO transport mode

```sh
uvx oracle.oci-object-storage-mcp-server
```

### HTTP streaming transport mode

```sh
ORACLE_MCP_HOST=<bind_host> \
ORACLE_MCP_PORT=<port> \
ORACLE_MCP_BASE_URL=<public_base_url> \
OCI_REGION=<region> \
IDCS_DOMAIN=<idcs_domain> \
IDCS_CLIENT_ID=<client_id> \
IDCS_CLIENT_SECRET=<client_secret> \
IDCS_AUDIENCE=<audience> \
uvx oracle.oci-object-storage-mcp-server
```

Register `${ORACLE_MCP_BASE_URL}/auth/callback` in the OCI IAM confidential application. If `IDCS_REQUIRED_SCOPES` is unset, the default is `openid profile email oci_mcp.object_storage.invoke`.

FastMCP 4.2.2 dynamically registers MCP OAuth clients as public clients. Clients that declare `application_type: web` must register a non-loopback HTTPS redirect URI. Native MCP clients can register a loopback HTTP redirect URI.

## Tools

| Tool Name | Description |
| --- | --- |
| get_namespace | Get the object storage namespace for the tenancy |
| list_buckets | List object storage buckets in a given compartment |
| get_bucket_details | Get details for a specific object storage bucket |
| list_objects | List objects in a given object storage bucket |
| list_object_versions | List object versions in a given object storage bucket |
| get_object | Return bounded object content and metadata directly to the client |
| upload_object | Upload an object to an object storage bucket |

⚠️ **NOTE**: `stdio` uses the configured OCI CLI profile. HTTP uses the authenticated OCI IAM user and does not use the local OCI CLI profile for request authentication.

### `get_object` response and limits

`get_object` accepts `bucket_name`, `compartment_id`, `object_name`, and the optional
`version_id`. It resolves the namespace automatically and returns an `ObjectContent`
result directly to the MCP client in both STDIO and HTTP modes. It does not write a
file on the server.

**Response contract change:** `get_object` now returns `ObjectContent` instead of
the previously advertised `ObjectSummary`. The SDK returns a streamed body, not an
object-summary model; the previous conversion failed for real downloads. Consumers
should use the schema below. `list_objects` still returns object summaries.

| Field | Meaning |
| --- | --- |
| `namespace`, `bucket_name`, `name` | Required object identity. `name` preserves the existing object-name field. |
| `size` | Required actual byte count of the body read, before converting it to UTF-8 text or base64. |
| `content` | Required string containing the entire object in the representation specified by `encoding`. |
| `encoding` | Required `"utf-8"` or `"base64"`; see the encoding rules below. |
| `etag`, `md5`, `time_modified`, `storage_tier`, `version_id` | Available service metadata, or `null`. `md5` comes from `Content-MD5`; `time_modified` is the `Last-Modified` timestamp serialized as an ISO 8601 datetime. |
| `content_type`, `content_encoding` | Original `Content-Type` and HTTP `Content-Encoding` headers, or `null`. `content_encoding` is distinct from the result's `encoding`. |
| `metadata` | User-defined metadata from `opc-meta-*` headers, with lowercase keys and the prefix removed; `{}` if absent. |

For example, a five-byte text object produces:

```json
{
  "namespace": "example_namespace",
  "bucket_name": "example-bucket",
  "name": "hello.txt",
  "size": 5,
  "content": "hello",
  "encoding": "utf-8",
  "etag": "example-etag",
  "md5": null,
  "time_modified": "2026-11-17T14:09:37Z",
  "storage_tier": null,
  "version_id": "example-version",
  "content_type": "text/plain; charset=utf-8",
  "content_encoding": null,
  "metadata": {}
}
```

Encoding rules:

- Text media types (`text/*`, `application/json`, `application/xml`, and types ending
  in `+json` or `+xml`) are decoded strictly when the charset is UTF-8 or ASCII.
  An omitted charset defaults to UTF-8. Successful text results use
  `encoding: "utf-8"`; encoding that string as UTF-8 recovers the original bytes.
- Binary or unknown media types, missing `Content-Type`, unsupported charsets, and
  text that cannot be decoded strictly use `encoding: "base64"`. Base64-decoding
  `content` recovers the original bytes without character replacement.
- Bodies with a non-identity HTTP `Content-Encoding`, such as `gzip`, are returned
  as base64 of the original encoded bytes. They are not automatically decompressed.
- Empty objects return `size: 0` and `content: ""`, with `encoding` selected by the
  same rules.

The server enforces a fixed **1 MiB (1,048,576 bytes)** object-body limit. It reads
in bounded chunks and at most one additional byte to detect an oversized object.
Neither limit enforcement nor `size` trusts `Content-Length`, including when that
header is missing or inaccurate. Oversized objects produce a tool error without
returning partial content or silently truncating the object. The streamed body is
closed on success and failure.

The limit applies to the original body bytes, including compressed bytes when
`Content-Encoding` is present. Base64, JSON escaping, and metadata can make the
serialized MCP response larger than 1 MiB; this is not a serialized-response or
model-token limit.

## Third-Party APIs

Developers choosing to distribute a binary implementation of this project are responsible for obtaining and providing all required licenses and copyright notices for the third-party code used in order to ensure compliance with their respective open source licenses.

## Disclaimer

Users are responsible for their local environment and credential safety. Different language model selections may yield different results and performance.

## Upload root

`upload_object` only reads files under `OCI_MCP_UPLOAD_ROOT` (default: `<tmpdir>/oci-mcp-uploads`). Set this to the directory you intend to upload from. Paths outside the root, and paths under `~/.oci`, `~/.ssh`, `/etc`, `/run/secrets`, or `/var/run/secrets`, are rejected.

## License

Copyright (c) 2025 Oracle and/or its affiliates.
 
Released under the Universal Permissive License v1.0 as shown at  
<https://oss.oracle.com/licenses/upl/>.
