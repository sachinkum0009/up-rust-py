"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import pytest
import time
from threading import Event

from up_rust_py import StaticUriProvider
from up_rust_py.communication import SimpleNotifier, UPayload
from up_rust_py.local_transport import LocalTransport, UStatusError


class TestSimpleNotifier:
    """Tests for SimpleNotifier"""

    def test_create_notifier(self):
        """Test creating a SimpleNotifier instance"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()

        notifier = SimpleNotifier(transport, uri_provider)

        assert notifier is not None
        assert hasattr(notifier, "notify")
        assert hasattr(notifier, "start_listening")
        assert hasattr(notifier, "stop_listening")

    def test_notifier_start_listening(self):
        """Test starting to listen for notifications"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        received_messages = []

        def listener(msg):
            text = msg.extract_string()
            if text:
                received_messages.append(text)

        topic = uri_provider.get_resource_uri(0xd100)

        # Should not raise an exception
        notifier.start_listening(topic, listener)

    def test_notifier_stop_listening(self):
        """Test stopping listening for notifications"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        def listener(msg):
            pass

        topic = uri_provider.get_resource_uri(0xd100)

        notifier.start_listening(topic, listener)

        # Should not raise an exception
        notifier.stop_listening(topic, listener)

    def test_notifier_send_notification(self):
        """Test sending a notification"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        payload = UPayload.from_string("Test notification")
        destination = uri_provider.get_source_uri()
        resource_id = 0xd100

        # Should not raise an exception
        notifier.notify(resource_id, destination, payload)

    def test_notifier_full_flow(self):
        """Test complete notification flow: listen, send, receive"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        received_messages = []
        message_received = Event()

        def listener(msg):
            text = msg.extract_string()
            if text:
                received_messages.append(text)
                message_received.set()

        # Start listening
        resource_id = 0xd100
        topic = uri_provider.get_resource_uri(resource_id)
        notifier.start_listening(topic, listener)

        # Give time for listener to be registered
        time.sleep(0.1)

        # Send notification
        test_message = "Hello from notifier!"
        payload = UPayload.from_string(test_message)
        destination = uri_provider.get_source_uri()
        notifier.notify(resource_id, destination, payload)

        # Wait for message
        received = message_received.wait(timeout=1.0)

        # Cleanup
        notifier.stop_listening(topic, listener)

        # Verify
        assert received, "Message was not received"
        assert test_message in received_messages

    def test_notifier_multiple_messages(self):
        """Test sending multiple notifications"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        received_messages = []

        def listener(msg):
            text = msg.extract_string()
            if text:
                received_messages.append(text)

        resource_id = 0xd100
        topic = uri_provider.get_resource_uri(resource_id)
        notifier.start_listening(topic, listener)

        time.sleep(0.1)

        # Send multiple notifications
        destination = uri_provider.get_source_uri()
        for i in range(3):
            message = f"Notification {i+1}"
            payload = UPayload.from_string(message)
            notifier.notify(resource_id, destination, payload)
            time.sleep(0.05)

        # Wait for messages to be processed
        time.sleep(0.2)

        notifier.stop_listening(topic, listener)

        assert len(received_messages) == 3
        assert "Notification 1" in received_messages
        assert "Notification 2" in received_messages
        assert "Notification 3" in received_messages

    def test_notifier_with_none_payload(self):
        """Test sending notification with None payload"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        destination = uri_provider.get_source_uri()
        resource_id = 0xd100

        # Should not raise an exception
        notifier.notify(resource_id, destination, None)

    def test_notifier_with_bytes_payload(self):
        """Test sending notification with bytes payload"""
        uri_provider = StaticUriProvider("test-vehicle", 0xa34b, 0x01)
        transport = LocalTransport()
        notifier = SimpleNotifier(transport, uri_provider)

        received_count = [0]

        def listener(msg):
            received_count[0] += 1

        resource_id = 0xd100
        topic = uri_provider.get_resource_uri(resource_id)
        notifier.start_listening(topic, listener)

        time.sleep(0.1)

        # Send with bytes payload
        payload = UPayload.from_bytes([0x48, 0x65, 0x6c, 0x6c, 0x6f])
        destination = uri_provider.get_source_uri()
        notifier.notify(resource_id, destination, payload)

        time.sleep(0.2)

        notifier.stop_listening(topic, listener)

        assert received_count[0] > 0


if __name__ == '__main__':
    pytest.main([__file__, "-v"])
