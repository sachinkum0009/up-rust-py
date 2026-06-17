"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

class UStatusError(Exception):
    """
    Exception raised when a uProtocol operation fails with a UStatus.

    Attributes:
        code: The symbolic UCode value name (for example, "ALREADY_EXISTS").
        message: The status message reported by the transport.
    """

    code: str
    message: str
    ...

class RegistrationError(Exception):
    """
    Exception raised when listener registration or unregistration fails.

    Attributes:
        kind: The registration error category.
        message: Human-readable registration error message.
        code: Optional symbolic UCode name when available.
    """

    kind: str
    message: str
    code: str
    ...

class UUri:
    """
    UUri Class
    """

    ...

class StaticUriProvider:
    """
    Provides URI information for uProtocol entities.

    StaticUriProvider creates and manages URIs for identifying entities
    in the uProtocol network. It combines an authority (device/vehicle name),
    entity ID, and version to create unique identifiers.
    """

    def __init__(self, authority: str, entity_id: int, version: int) -> None:
        """
        Create a new StaticUriProvider.

        Args:
            authority: The authority name identifying the device/vehicle
                      (e.g., "my-vehicle", "sensor-001").
            entity_id: The entity ID (0 to 2^32-1, e.g., 0xa34b).
            version: The version number (0 to 255, e.g., 0x01).

        Example:
            >>> from up_rust_py import StaticUriProvider
            >>> provider = StaticUriProvider("my-vehicle", 0xa34b, 0x01)
        """
        ...

    def get_resource_uri(self, resource_id: int) -> UUri:
        """
        Get a resource URI for a specific resource ID.

        Args:
            resource_id: The resource ID (0 to 65535).

        Returns:
            The resource URI.

        Example:
            >>> topic = provider.get_resource_uri(0xd100)
        """
        ...

    def get_source_uri(self) -> UUri:
        """
        Get the source URI for this entity.

        Returns:
            The source URI identifying this entity.

        Example:
            >>> source = provider.get_source_uri()
        """
        ...

class UMessage:
    """
    Represents a complete uProtocol message.

    UMessage encapsulates both the payload and metadata for a uProtocol communication.
    It is typically received by listener callbacks.
    """

    def extract_string(self) -> Optional[str]:
        """
        Extract string value from the message payload.

        Returns:
            The extracted string if successful, None if the message
            doesn't contain a string value.

        Example:
            >>> text = message.extract_string()
            >>> if text:
            ...     print(f"Received: {text}")
        """
        ...

    def get_payload(self) -> Optional[bytes]:
        """Get the raw payload bytes

        Returns:
            bytes | None: The raw payload, or None if the message has no payload.
        """

    def get_attributes(self) -> Optional[UAttributes]:
        """Get the attributes of UMessage"""
        ...

class UUID:
    """Represents UUID"""
    def get_msb(self) -> int:
        """return msb"""
        ...
    def get_lsb(self) -> int:
        """return lsb"""
        ...

# TODO(Sachin): I think I should probably add function to reterive the enum
class UMessageType:
    """Represents UMessageType"""

class UPriority:
    """Represents UPriority"""

class UCode:
    """Represents UCode"""

class UPayloadFormat:
    """Represents UPayloadFormat"""

class UAttributes:
    """Represents UAttributes"""
    def get_id(self) -> Optional[UUID]:
        """returns the UUID"""
        ...

    def get_type_(self) -> Optional[UMessageType]:
        """return type_"""
        ...

    def get_source(self) -> Optional[UUri]:
        """return source"""
        ...

    def get_sink(self) -> Optional[UUri]:
        """return sink"""
        ...

    def get_priority(self) -> Optional[UPriority]:
        """return priority"""
        ...

    def get_ttl(self) -> int:
        """return ttl"""

    def get_permission_level(self) -> int:
        """return permission level"""

    def get_commstatus(self) -> UCode:
        """retun commstatus"""

    def get_reqid(self) -> Optional[UUID]:
        """return reqid"""

    def get_token(self) -> str:
        """return token"""

    def get_traceparent(self) -> str:
        """return traceparent"""

    def get_payload_format(self) -> Optional[UPayloadFormat]:
        """return payload format"""

__version__: str
