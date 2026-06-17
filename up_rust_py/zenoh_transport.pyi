"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

"""Type stubs for Zenoh Transport"""

from typing import Callable, Optional

from . import UMessage, UUri

class UPTransportZenoh:
    """Zenoh-based network transport for uProtocol.

    Provides publish/subscribe capabilities across network boundaries using
    the Zenoh protocol. Unlike LocalTransport which only works within a single
    process, UPTransportZenoh enables distributed communication.
    """

    @staticmethod
    def builder(authority: str) -> UPTransportZenohBuilder:
        """Create a new builder for UPTransportZenoh.

        Args:
            authority: The authority name (e.g., "my-vehicle", "device-123")

        Returns:
            A builder instance to configure the transport

        Example:
            >>> builder = UPTransportZenoh.builder("my-vehicle")
            >>> transport = builder.build()
        """
        ...

    def send(self, message: UMessage) -> None:
        """Send a UMessage via Zenoh transport.

        Args:
            message: The UMessage to send

        Raises:
            Exception: If sending fails

        Example:
            >>> transport.send(message)
        """
        ...

    def register_listener(
        self,
        source_filter: UUri,
        sink_filter: Optional[UUri],
        listener: Callable[[UMessage], None],
    ) -> None:
        """Register a listener for messages matching the source filter.

        Args:
            source_filter: The URI to listen for messages from
            sink_filter: The sink address pattern that messages need to match, or None to match messages that do not contain any sink address.
            listener: Python callable that receives UMessage objects

        Raises:
            Exception: If registration fails

        Example:
            >>> def handle_message(msg):
            ...     print(f"Received: {msg.extract_string()}")
            >>> transport.register_listener(source_uri, handle_message)
        """
        ...

    def unregister_listener(
        self,
        source_filter: UUri,
        sink_filter: Optional[UUri],
        listener: Callable[[UMessage], None],
    ) -> None:
        """Unregister a listener for the given source filter.

        Args:
            source_filter: The URI to stop listening to
            sink_filter: The sink address pattern that messages need to match, or None to match messages that do not contain any sink address.
            listener: The Python callable that was registered

        Raises:
            Exception: If unregistration fails

        Note:
            Due to listener instance comparison issues, this may not work as expected.
            Consider letting listeners be cleaned up automatically.

        Example:
            >>> transport.unregister_listener(source_uri, handle_message)
        """
        ...

class UPTransportZenohBuilder:
    """Builder for configuring and creating UPTransportZenoh instances.

    Provides a fluent API for setting up Zenoh transport configuration.
    """

    def build(self) -> UPTransportZenoh:
        """Build the UPTransportZenoh instance.

        Returns:
            The configured transport instance

        Raises:
            Exception: If building fails

        Example:
            >>> transport = UPTransportZenoh.builder("my-vehicle").build()
        """
        ...
