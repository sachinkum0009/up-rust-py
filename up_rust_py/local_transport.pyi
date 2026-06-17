from up_rust_py import UUri

"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Callable, Optional

from . import StaticUriProvider, UMessage, UStatusError

class LocalTransport:
    """
    Provides local (in-process) transport for uProtocol communication.

    LocalTransport enables communication between components within the same
    process without network overhead. It manages listener registration and
    message routing.
    """

    def __init__(self) -> None:
        """
        Create a new LocalTransport instance.

        Raises:
            Exception: If the runtime creation fails.

        Example:
            >>> from up_rust_py.local_transport import LocalTransport
            >>> transport = LocalTransport()
        """
        ...

    def register_listener(
        self,
        source_filter: UUri,
        sink_filter: Optional[UUri],
        listener: Callable[[UMessage], None],
    ) -> None:
        """
        Registers a listener to be called for messages.

        The listener will be invoked for each message that matches the given source and sink filter patterns
        according to the rules defined by the [UUri specification](https://github.com/eclipse-uprotocol/up-spec/blob/v1.6.0-alpha.7/basics/uri.adoc).

        Args:
            source_filter: The URI provider identifying the entity.
            sink_filter: The resource ID to listen to (0 to 65535).
            listener: A Python function that accepts a UMessage parameter.
                        Will be called when messages arrive.

        Raises:
            UStatusError: If registration fails.

        Example:
            >>> from up_rust_py import UMessage
            >>> def my_handler(msg: UMessage):
            ...     print(msg.extract_string())
            >>> transport.register_listener(uri_provider, 0xb4c1, my_handler)
        """
        ...

    def unregister_listener(
        self,
        source_filter: UUri,
        sink_filter: Optional[UUri],
        listener: Callable[[UMessage], None],
    ) -> None:
        """
        Deregisters a message listener.

        The listener will no longer be called for any (matching) messages after this function has
        returned successfully.

        Args:
            source_filter: The _source_ address pattern that the listener had been registered for.
            sink_filter: The _sink_ address pattern that the listener had been registered for.
            listener: The listener to unregister.

        Raises:
            UStatusError: If unregistration fails or listener not found.
        """
        ...
