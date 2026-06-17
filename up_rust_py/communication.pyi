"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional, Callable
from . import StaticUriProvider, UUri, UMessage, RegistrationError
from .local_transport import LocalTransport
from .zenoh_transport import UPTransportZenoh


class UPayload:
    """
    Represents a message payload in uProtocol.

    UPayload encapsulates the data being transmitted in a uProtocol message.
    It can be created from strings or raw bytes.
    """

    @staticmethod
    def from_string(value: str) -> 'UPayload':
        """
        Create a UPayload from a string value.

        Args:
            value: The string content to wrap in the payload.

        Returns:
            A new payload instance containing the string.

        Raises:
            Exception: If the payload creation fails.

        Example:
            >>> from up_rust_py.communication import UPayload
            >>> payload = UPayload.from_string("Hello, World!")
        """
        ...

    @staticmethod
    def from_bytes(data: list[int]) -> 'UPayload':
        """
        Create a UPayload from raw bytes.

        Args:
            data: A list of bytes (0-255) to wrap in the payload.

        Returns:
            A new payload instance containing the binary data.

        Example:
            >>> from up_rust_py.communication import UPayload
            >>> payload = UPayload.from_bytes([72, 101, 108, 108, 111])
        """
        ...

class SimplePublisher:
    """
    Publisher for sending uProtocol messages.

    SimplePublisher provides an easy-to-use interface for publishing messages
    to specific resources in the uProtocol network.
    """

    def __init__(self, transport: 'LocalTransport' | 'UPTransportZenoh', uri_provider: StaticUriProvider) -> None:
        """
        Create a new SimplePublisher.

        Args:
            transport: The transport to use for sending messages.
            uri_provider: The URI provider for the publishing entity.

        Raises:
            Exception: If the runtime creation fails.

        Example:
            >>> from up_rust_py.communication import SimplePublisher
            >>> from up_rust_py.local_transport import LocalTransport
            >>> from up_rust_py import StaticUriProvider
            >>> transport = LocalTransport()
            >>> provider = StaticUriProvider("device", 0x1234, 0x01)
            >>> publisher = SimplePublisher(transport, provider)
        """
        ...

    def publish(self, resource_id: int, payload: Optional['UPayload']) -> None:
        """
        Publish a message to a specific resource.

        Args:
            resource_id: The target resource ID (0 to 65535).
            payload: The message payload, or None for empty messages.

        Raises:
            Exception: If publishing fails.

        Example:
            >>> from up_rust_py.communication import UPayload
            >>> payload = UPayload.from_string("Hello")
            >>> publisher.publish(0xb4c1, payload)
            >>> # Or publish without payload:
            >>> publisher.publish(0xb4c1, None)
        """
        ...

class SimpleNotifier:
    """
    A Notifier that uses the uProtocol Transport Layer API to send and receive notifications to/from (other) uEntities.

    SimpleNotifier provides an easy-to-use interface for sending notifications
    and listening for notifications from other entities in the uProtocol network.
    """
    def __init__(self, transport: LocalTransport, uri_provider: StaticUriProvider) -> None:
        """
        Create a new SimpleNotifier.

        Args:
            transport: The transport to use for sending and receiving notifications.
            uri_provider: The URI provider for the notifying entity.

        Raises:
            Exception: If the runtime creation fails.

        Example:
            >>> from up_rust_py.communication import SimpleNotifier
            >>> from up_rust_py.local_transport import LocalTransport
            >>> from up_rust_py import StaticUriProvider
            >>> transport = LocalTransport()
            >>> provider = StaticUriProvider("my-vehicle", 0xa34b, 0x01)
            >>> notifier = SimpleNotifier(transport, provider)
        """
        ...

    def start_listening(self, topic: UUri, callback: Callable[[UMessage], None]) -> None:
        """
        Start listening for notifications on a specific topic.

        Args:
            topic: The topic URI to listen to.
            callback: A Python function that accepts a UMessage parameter.
                     Will be called when notifications arrive.

        Raises:
            RegistrationError: If listener registration fails.

        Example:
            >>> from up_rust_py import UMessage
            >>> def notification_handler(msg: UMessage):
            ...     text = msg.extract_string()
            ...     if text:
            ...         print(f"Notification: {text}")
            >>> topic = uri_provider.get_resource_uri(0xd100)
            >>> notifier.start_listening(topic, notification_handler)
        """
        ...

    def stop_listening(self, topic: UUri, callback: Callable[[UMessage], None]) -> None:
        """
        Stop listening for notifications on a specific topic.

        Args:
            topic: The topic URI to stop listening to.
            callback: The same Python function that was registered.

        Raises:
            RegistrationError: If listener unregistration fails.

        Example:
            >>> notifier.stop_listening(topic, notification_handler)
        """
        ...

    def notify(self, resource_id: int, destination: UUri, payload: Optional[UPayload]) -> None:
        """
        Send a notification to a specific destination.

        Args:
            resource_id: The notification resource ID (0 to 65535).
            destination: The destination URI to send the notification to.
            payload: The notification payload, or None for empty notifications.

        Raises:
            Exception: If notification sending fails.

        Example:
            >>> from up_rust_py.communication import UPayload
            >>> payload = UPayload.from_string("Alert!")
            >>> destination = uri_provider.get_source_uri()
            >>> notifier.notify(0xd100, destination, payload)
        """
        ...
