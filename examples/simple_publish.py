"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from up_rust_py import StaticUriProvider
from up_rust_py.communication import SimplePublisher, UMessage, UPayload
from up_rust_py.local_transport import LocalTransport

ORIGIN_RESOURCE_ID = 0xB4C1


def console_printer(msg: UMessage):
    text = msg.extract_string()
    if text:
        print(f"  received: {text}")
    bytes = msg.get_payload()
    if bytes:
        print(f"  payload bytes: {bytes}")

    attributes = msg.get_attributes()
    if attributes:
        id = attributes.get_id()
        if id:
            lsb = id.get_lsb()
            print(f"lsb: {lsb}")


def main():
    uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
    uuri = uri_provider.get_resource_uri(ORIGIN_RESOURCE_ID)
    print(f"Using URI: {uuri}")

    transport = LocalTransport()

    transport.register_listener(uuri, None, console_printer)

    publisher = SimplePublisher(transport, uri_provider)

    # Create and publish payload
    print("Publishing message...")
    payload = UPayload.from_string("Hello from Python!")
    publisher.publish(ORIGIN_RESOURCE_ID, payload)

    print("Done!")


if __name__ == "__main__":
    main()
