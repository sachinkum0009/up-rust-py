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
from up_rust_py.communication import SimplePublisher, UPayload
from up_rust_py.zenoh_transport import UPTransportZenoh


def main():
    print("uProtocol Zenoh Publisher Example")
    print("=" * 60)

    # Create Zenoh transport
    print("\n1. Building Zenoh transport...")
    transport = UPTransportZenoh.builder("my-vehicle").build()
    print("   ✓ Zenoh transport created")

    # Create URI provider for our entity
    print("\n2. Creating URI provider...")
    authority = "my-vehicle"
    entity_id = 0xA34B  # Example entity ID
    version = 0x01
    uri_provider = StaticUriProvider(authority, entity_id, version)
    print(f"   ✓ URI provider created: {authority}/{hex(entity_id)}/{hex(version)}")

    # Create SimplePublisher with Zenoh transport
    print("\n3. Creating publisher with Zenoh transport...")
    publisher = SimplePublisher(transport, uri_provider)
    print("   ✓ Publisher created successfully")

    # Publish messages
    print("\n4. Publishing messages...")
    resource_id = 0x8001

    # Publish 5 messages
    for i in range(5):
        message = f"Hello from Zenoh publisher! Message #{i + 1}"
        payload = UPayload.from_string(message)

        print(f"   📤 Publishing: {message}")
        publisher.publish(resource_id, payload)

        time.sleep(1)  # Wait 1 second between messages

    print("\n✓ Successfully published 5 messages via Zenoh!")
    print("\nTo receive these messages, run:")
    print("  uv run python examples/simple_zenoh_subscriber.py")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
