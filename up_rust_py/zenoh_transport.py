"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

"""Zenoh Transport for uProtocol

This module provides network transport capabilities using the Zenoh protocol.
Zenoh enables efficient, real-time communication across network boundaries.

Classes:
    UPTransportZenoh: Main transport class for Zenoh-based communication
    UPTransportZenohBuilder: Builder for configuring Zenoh transport

Example:
    >>> from up_rust_py.zenoh_transport import UPTransportZenoh
    >>> transport = UPTransportZenoh.builder("my-vehicle").build()
    >>> # Use transport.send() to publish messages
"""

try:
    from up_rust_py import zenoh_transport as _zenoh_transport

    UPTransportZenoh = _zenoh_transport.UPTransportZenoh
    UPTransportZenohBuilder = _zenoh_transport.UPTransportZenohBuilder

    __all__ = ["UPTransportZenoh", "UPTransportZenohBuilder"]
except (ImportError, AttributeError) as e:
    raise ImportError(
        "Zenoh transport not available. "
        "The package was not built with zenoh support. "
        "Please install a version built with zenoh features enabled."
    ) from e
