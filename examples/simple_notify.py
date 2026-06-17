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
from up_rust_py.communication import RegistrationError, SimpleNotifier, UPayload
from up_rust_py.local_transport import LocalTransport


def console_printer(msg):
    """
    Callback function that prints received notification messages.

    Args:
        msg: The UMessage containing the notification payload.
    """
    text = msg.extract_string()
    if text:
        print(f"Received notification: {text}")


def main():
    ORIGIN_RESOURCE_ID = 0xD100

    uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)

    transport = LocalTransport()

    notifier = SimpleNotifier(transport, uri_provider)

    topic = uri_provider.get_resource_uri(ORIGIN_RESOURCE_ID)

    print("Starting to listen for notifications...")
    try:
        notifier.start_listening(topic, console_printer)
    except RegistrationError as e:
        print(f"Error starting listener: {e}")

    payload = UPayload.from_string("Hello from Python!")

    destination = uri_provider.get_source_uri()
    print("Sending notification...")
    try:
        notifier.notify(ORIGIN_RESOURCE_ID, destination, payload)
    except RegistrationError as e:
        print(f"Error sending notification: {e}")

    # Stop listening (cleanup)
    print("Stopping listener...")
    try:
        notifier.stop_listening(topic, console_printer)
    except RegistrationError as e:
        print(f"Error stopping listener: {e}")

    print("Done!")


if __name__ == "__main__":
    main()
