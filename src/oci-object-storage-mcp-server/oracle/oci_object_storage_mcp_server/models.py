"""
Copyright (c) 2025, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""

from base64 import b64encode
from datetime import datetime
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Literal, Mapping, Optional

import oci.object_storage.models
from pydantic import BaseModel, ConfigDict, Field


class Bucket(BaseModel):
    namespace: Optional[str] = Field(
        None,
        description=("The Object Storage namespace in which the bucket resides."),
    )
    name: Optional[str] = Field(
        None,
        description="The name of the bucket.",
    )
    compartment_id: Optional[str] = Field(
        None,
        description=("The compartment ID in which the bucket is authorized."),
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description=("Arbitrary string keys and values for user-defined metadata."),
    )
    created_by: Optional[str] = Field(
        None,
        description="The OCID of the user who created the bucket.",
    )
    time_created: Optional[datetime] = Field(
        None,
        description="The date and time the bucket was created.",
    )
    etag: Optional[str] = Field(
        None,
        description="The entity tag (ETag) for the bucket.",
    )
    public_access_type: Optional[str] = Field(
        None,
        description=("The type of public access enabled on this bucket."),
    )
    storage_tier: Optional[str] = Field(
        None,
        description="The storage tier type assigned to the bucket.",
    )
    object_events_enabled: Optional[bool] = Field(
        None,
        description=("Whether or not events are emitted for object state changes in this bucket."),
    )
    freeform_tags: Optional[Dict[str, str]] = Field(
        None,
        description="Free-form tags for this resource.",
    )
    defined_tags: Optional[Dict[str, Dict[str, object]]] = Field(
        None,
        description="Defined tags for this resource.",
    )
    kms_key_id: Optional[str] = Field(
        None,
        description=("The OCID of a master encryption key used to call the Key Management service."),
    )
    object_lifecycle_policy_etag: Optional[str] = Field(
        None,
        description=("The entity tag (ETag) for the live object lifecycle policy on the bucket."),
    )
    approximate_count: Optional[int] = Field(
        None,
        description="The approximate number of objects in the bucket.",
    )
    approximate_size: Optional[int] = Field(
        None,
        description=("The approximate total size in bytes of all objects in the bucket."),
    )
    replication_enabled: Optional[bool] = Field(
        None,
        description="Whether or not this bucket is a replication source.",
    )
    is_read_only: Optional[bool] = Field(
        None,
        description="Whether or not this bucket is read only.",
    )
    id: Optional[str] = Field(
        None,
        description="The OCID of the bucket.",
    )
    versioning: Optional[str] = Field(
        None,
        description="The versioning status on the bucket.",
    )
    auto_tiering: Optional[str] = Field(
        None,
        description="The auto tiering status on the bucket.",
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class NamespaceMetadata(BaseModel):
    """
    Pydantic model mirroring the fields of oci.object_storage.models.NamespaceMetadata.
    """

    namespace: str = Field(
        ...,
        description=("The Object Storage namespace to which the metadata belongs."),
    )
    default_s3_compartment_id: Optional[str] = Field(
        None,
        description=(
            "If set, specifies the default compartment assignment for the Amazon S3 Compatibility API."
        ),
    )
    default_swift_compartment_id: Optional[str] = Field(
        None,
        description=("If set, specifies the default compartment assignment for the Swift API."),
    )

    model_config = ConfigDict(extra="forbid")


class CreateBucketDetails(BaseModel):
    """
    Pydantic model mirroring the fields of
    oci.object_storage.models.CreateBucketDetails.
    """

    name: str = Field(
        ...,
        description="The name of the bucket.",
    )
    compartment_id: str = Field(
        ...,
        description=("The ID of the compartment in which to create the bucket."),
    )
    metadata: Optional[Dict[str, str]] = Field(
        None,
        description=("Arbitrary string, up to 4KB, of keys and values for user-defined metadata."),
    )
    public_access_type: Optional[str] = Field(
        None,
        description=("The type of public access enabled on this bucket."),
    )
    storage_tier: Optional[str] = Field(
        None,
        description="The type of storage tier of this bucket.",
    )
    object_events_enabled: Optional[bool] = Field(
        None,
        description=("Whether or not events are emitted for object state changes in this bucket."),
    )
    freeform_tags: Optional[Dict[str, str]] = Field(
        None,
        description="Free-form tags for this resource.",
    )
    defined_tags: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Defined tags for this resource.",
    )
    kms_key_id: Optional[str] = Field(
        None,
        description=("The OCID of a master encryption key used to call the Key Management service."),
    )
    versioning: Optional[str] = Field(
        None,
        description="The versioning status on the bucket.",
    )
    auto_tiering: Optional[str] = Field(
        None,
        description="The auto tiering status on the bucket.",
    )

    model_config = ConfigDict(extra="forbid")


class BucketSummary(BaseModel):
    namespace: Optional[str] = Field(
        None,
        description=("The Object Storage namespace in which the bucket lives."),
    )
    name: Optional[str] = Field(
        None,
        description="The name of the bucket.",
    )
    compartment_id: Optional[str] = Field(
        None,
        description=("The compartment ID in which the bucket is authorized."),
    )
    created_by: Optional[str] = Field(
        None,
        description="The OCID of the user who created the bucket.",
    )
    time_created: Optional[datetime] = Field(
        None,
        description="The date and time the bucket was created.",
    )
    etag: Optional[str] = Field(
        None,
        description="The entity tag (ETag) for the bucket.",
    )
    freeform_tags: Optional[Dict[str, str]] = Field(
        None,
        description="Free-form tags for this resource.",
    )
    defined_tags: Optional[Dict[str, Dict[str, object]]] = Field(
        None,
        description="Defined tags for this resource.",
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class ObjectSummary(BaseModel):
    name: Optional[str] = Field(
        None,
        description="The name of the object.",
    )
    size: Optional[int] = Field(
        None,
        description="Size of the object in bytes.",
    )
    md5: Optional[str] = Field(
        None,
        description="Base64-encoded MD5 hash of the object data.",
    )
    time_created: Optional[datetime] = Field(
        None,
        description="The date and time the object was created.",
    )
    etag: Optional[str] = Field(
        None,
        description="The current entity tag (ETag) for the object.",
    )
    storage_tier: Optional[str] = Field(
        None,
        description="The storage tier that the object is stored in.",
    )
    archival_state: Optional[str] = Field(
        None,
        description="Archival state of an object.",
    )
    time_modified: Optional[datetime] = Field(
        None,
        description="The date and time the object was modified.",
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class ObjectContent(BaseModel):
    """Bounded object content and metadata returned by get_object."""

    namespace: str = Field(..., description="The Object Storage namespace containing the object.")
    bucket_name: str = Field(..., description="The name of the bucket containing the object.")
    name: str = Field(..., description="The name of the object.")
    size: int = Field(
        ..., ge=0, description="The actual number of object bytes read, before content encoding."
    )
    content: str = Field(..., description="The complete object content, represented according to encoding.")
    encoding: Literal["utf-8", "base64"] = Field(
        ..., description="UTF-8 text or lossless base64 encoding of the original object bytes."
    )
    etag: Optional[str] = Field(None, description="The entity tag (ETag) returned by Object Storage.")
    md5: Optional[str] = Field(None, description="The service-provided base64 Content-MD5, when available.")
    time_modified: Optional[datetime] = Field(None, description="The object's Last-Modified timestamp.")
    storage_tier: Optional[str] = Field(None, description="The storage tier returned by Object Storage.")
    version_id: Optional[str] = Field(None, description="The object version ID returned by Object Storage.")
    content_type: Optional[str] = Field(None, description="The original Content-Type header, if available.")
    content_encoding: Optional[str] = Field(
        None, description="The original HTTP Content-Encoding, distinct from the result's encoding."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="User-defined object metadata, with the opc-meta- prefix removed."
    )

    model_config = ConfigDict(extra="forbid")


def map_object_content(
    namespace: str,
    bucket_name: str,
    name: str,
    data: bytes,
    headers: Mapping[str, str],
) -> ObjectContent:
    """Convert already-bounded, undecoded SDK response bytes into a transport-independent result."""
    headers = {key.lower(): value for key, value in headers.items()}
    message = Message()
    message["content-type"] = headers.get("content-type", "application/octet-stream")
    media_type = headers.get("content-type", "").partition(";")[0].strip().lower()
    charset = message.get_content_charset("utf-8")
    is_text = (
        media_type.startswith("text/")
        or media_type in {"application/json", "application/xml"}
        or media_type.endswith(("+json", "+xml"))
    )
    content = None
    if (
        is_text
        and charset in {"utf-8", "utf8", "ascii", "us-ascii"}
        and headers.get("content-encoding", "identity").strip().lower() in {"", "identity"}
    ):
        try:
            content = data.decode(charset)
        except UnicodeDecodeError:
            pass  # Preserve undecodable text as bytes rather than replacing characters.

    last_modified = headers.get("last-modified")
    return ObjectContent(
        namespace=namespace,
        bucket_name=bucket_name,
        name=name,
        size=len(data),
        content=content if content is not None else b64encode(data).decode("ascii"),
        encoding="utf-8" if content is not None else "base64",
        etag=headers.get("etag"),
        md5=headers.get("content-md5"),
        time_modified=parsedate_to_datetime(last_modified) if last_modified else None,
        storage_tier=headers.get("storage-tier"),
        version_id=headers.get("version-id"),
        content_type=headers.get("content-type"),
        content_encoding=headers.get("content-encoding"),
        metadata={
            key.removeprefix("opc-meta-"): value
            for key, value in headers.items()
            if key.startswith("opc-meta-")
        },
    )


class ListObjects(BaseModel):
    objects: Optional[List[ObjectSummary]] = Field(
        None,
        description="An array of object summaries.",
    )
    prefixes: Optional[List[str]] = Field(
        None,
        description=(
            "Prefixes that are common to the results returned "
            "by the request if the request specified a delimiter."
        ),
    )
    next_start_with: Optional[str] = Field(
        None,
        description=(
            "The name of the object to use in the `start` "
            "parameter to obtain the next page of a truncated "
            "ListObjects response."
        ),
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class ObjectVersionSummary(BaseModel):
    name: Optional[str] = Field(
        None,
        description="The name of the object.",
    )
    size: Optional[int] = Field(
        None,
        description="Size of the object in bytes.",
    )
    md5: Optional[str] = Field(
        None,
        description="Base64-encoded MD5 hash of the object data.",
    )
    time_created: Optional[datetime] = Field(
        None,
        description="The date and time the object was created.",
    )
    time_modified: Optional[datetime] = Field(
        None,
        description="The date and time the object was modified.",
    )
    etag: Optional[str] = Field(
        None,
        description="The current entity tag (ETag) for the object.",
    )
    storage_tier: Optional[str] = Field(
        None,
        description="The storage tier that the object is stored in.",
    )
    archival_state: Optional[str] = Field(
        None,
        description="Archival state of an object.",
    )
    version_id: Optional[str] = Field(
        None,
        description="VersionId of the object.",
    )
    is_delete_marker: Optional[bool] = Field(
        None,
        description="This flag will indicate if the version is deleted or not.",
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class ObjectVersionCollection(BaseModel):
    """
    Pydantic model mirroring the fields of oci.object_storage.models.ObjectVersionCollection.
    """

    items: List[ObjectVersionSummary] = Field(..., description="An array of object version summaries.")
    prefixes: Optional[List[str]] = Field(
        None,
        description=(
            "Prefixes that are common to the results returned by the request if the request "
            "specified a delimiter."
        ),
    )

    model_config = ConfigDict(extra="forbid")


def map_object_summary(obj: oci.object_storage.models.ObjectSummary) -> ObjectSummary:
    """
    Convert an oci.object_storage.models.ObjectSummary to an
    oracle.oci_object_storage_mcp_server.models.ObjectSummary, including all nested types
    """
    return ObjectSummary(
        name=obj.name,
        size=getattr(obj, "size", None),
        time_created=getattr(obj, "time_created", None),
        etag=getattr(obj, "etag", None),
        storage_tier=getattr(obj, "storage_tier", None),
        archival_state=getattr(obj, "archival_state", None),
        time_modified=getattr(obj, "time_modified", None),
    )


def map_bucket_summary(
    bucket: oci.object_storage.models.BucketSummary,
) -> BucketSummary:
    """
    Convert an oci.object_storage.models.BucketSummary to an
    oracle.oci_object_storage_mcp_server.models.BucketSummary, including all nested types
    """
    return BucketSummary(
        namespace=getattr(bucket, "namespace", None),
        name=getattr(bucket, "name", None),
        compartment_id=getattr(bucket, "compartment_id", None),
        created_by=getattr(bucket, "created_by", None),
        time_created=getattr(bucket, "time_created", None),
        etag=getattr(bucket, "etag", None),
        freeform_tags=getattr(bucket, "freeform_tags", None),
        defined_tags=getattr(bucket, "defined_tags", None),
    )


def map_bucket(bucket: oci.object_storage.models.Bucket) -> Bucket:
    """
    Convert an oci.object_storage.models.Bucket to an oracle.oci_object_storage_mcp_server.models.Bucket,
    including all nested types
    """
    return Bucket(
        namespace=getattr(bucket, "namespace", None),
        name=getattr(bucket, "name", None),
        compartment_id=getattr(bucket, "compartment_id", None),
        metadata=getattr(bucket, "metadata", None),
        created_by=getattr(bucket, "created_by", None),
        time_created=getattr(bucket, "time_created", None),
        etag=getattr(bucket, "etag", None),
        public_access_type=getattr(bucket, "public_access_type", None),
        storage_tier=getattr(bucket, "storage_tier", None),
        object_events_enabled=getattr(bucket, "object_events_enabled", None),
        freeform_tags=getattr(bucket, "freeform_tags", None),
        defined_tags=getattr(bucket, "defined_tags", None),
        kms_key_id=getattr(bucket, "kms_key_id", None),
        object_lifecycle_policy_etag=getattr(bucket, "object_lifecycle_policy_etag", None),
        approximate_count=getattr(bucket, "approximate_count", None),
        approximate_size=getattr(bucket, "approximate_size", None),
        replication_enabled=getattr(bucket, "replication_enabled", None),
        is_read_only=getattr(bucket, "is_read_only", None),
        id=getattr(bucket, "id", None),
        versioning=getattr(bucket, "versioning", None),
        auto_tiering=getattr(bucket, "auto_tiering", None),
    )


def map_object_version_summary(obj: oci.object_storage.models.ObjectVersionSummary):
    return ObjectVersionSummary(
        name=obj.name,
        size=getattr(obj, "size", None),
        md5=getattr(obj, "md5", None),
        time_created=getattr(obj, "time_created", None),
        time_modified=getattr(obj, "time_modified", None),
        etag=getattr(obj, "etag", None),
        storage_tier=getattr(obj, "storage_tier", None),
        archival_state=getattr(obj, "archival_state", None),
        version_id=getattr(obj, "version_id", None),
        is_delete_marker=getattr(obj, "is_delete_marker", None),
    )
