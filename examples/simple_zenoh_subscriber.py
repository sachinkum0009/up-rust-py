"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import time

from up_rust_py import StaticUriProvider
from up_rust_py.zenoh_transport import UPTransportZenoh


def message_handler(msg):
    """Callback function to handle received messages."""
    text = msg.extract_string()
    if text:
        print(f"   📥 Received: {text}")
    else:
        print("   📥 Received message (non-string payload)")


def main():
    print("uProtocol Zenoh Subscriber Example")
    print("=" * 60)

    # Create Zenoh transport
    print("\n1. Building Zenoh transport...")
    transport = UPTransportZenoh.builder("my-vehicle").build()
    print("   ✓ Zenoh transport created")

    # Create URI provider (must match publisher's)
    print("\n2. Creating URI provider...")
    authority = "my-vehicle"
    entity_id = 0xA34B  # Must match publisher
    version = 0x01
    uri_provider = StaticUriProvider(authority, entity_id, version)
    print(f"   ✓ URI provider created: {authority}/{hex(entity_id)}/{hex(version)}")

    # Register listener for the same resource ID as publisher
    print("\n3. Registering listener...")
    resource_id = 0x8001
    transport.register_listener(
        uri_provider.get_resource_uri(resource_id), message_handler
    )
    print(f"   ✓ Listener registered for resource ID: {hex(resource_id)}")

    print("\n4. Waiting for messages...")
    print("   (Press Ctrl+C to stop)\n")

    # Keep running to receive messages
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✓ Subscriber stopped")
        print("=" * 60)


if __name__ == "__main__":
    main()
