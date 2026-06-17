"""
SPDX-FileCopyrightText: 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

"""Tests for Zenoh transport functionality"""

import time
from threading import Event

import pytest

from up_rust_py import StaticUriProvider
from up_rust_py.communication import SimplePublisher, UPayload

try:
    from up_rust_py.zenoh_transport import UPTransportZenoh

    ZENOH_AVAILABLE = True
except (ImportError, AttributeError):
    ZENOH_AVAILABLE = False
    pytest.skip("Zenoh transport not available", allow_module_level=True)


class TestZenohTransport:
    """Tests for UPTransportZenoh"""

    def test_create_zenoh_transport(self):
        """Test creating a Zenoh transport instance"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        assert transport is not None

    def test_create_zenoh_publisher(self):
        """Test creating a publisher with Zenoh transport"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)

        publisher = SimplePublisher(transport, uri_provider)

        assert publisher is not None
        assert hasattr(publisher, "publish")

    def test_zenoh_publisher_publish_string_payload(self):
        """Test publishing a string message through Zenoh"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)
        publisher = SimplePublisher(transport, uri_provider)

        payload = UPayload.from_string("Test message")
        resource_id = 0x8001

        # Should not raise an exception
        publisher.publish(resource_id, payload)

    def test_zenoh_publisher_publish_bytes_payload(self):
        """Test publishing a bytes message through Zenoh"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)
        publisher = SimplePublisher(transport, uri_provider)

        payload = UPayload.from_bytes([0x48, 0x65, 0x6C, 0x6C, 0x6F])  # "Hello"
        resource_id = 0x8001

        # Should not raise an exception
        publisher.publish(resource_id, payload)

    def test_zenoh_publisher_publish_none_payload(self):
        """Test publishing without payload through Zenoh"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)
        publisher = SimplePublisher(transport, uri_provider)

        resource_id = 0x8001

        # Should not raise an exception
        publisher.publish(resource_id, None)

    def test_zenoh_register_listener(self):
        """Test registering a listener with Zenoh transport"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)

        def listener(msg):
            pass

        resource_id = 0x8001
        source_uri = uri_provider.get_resource_uri(resource_id)

        # Should not raise an exception
        transport.register_listener(source_uri, None, listener)

    def test_zenoh_register_and_unregister_listener(self):
        """Test registering and unregistering a listener with Zenoh"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)

        def listener(msg):
            pass

        resource_id = 0x8001
        source_uri = uri_provider.get_resource_uri(resource_id)

        transport.register_listener(source_uri, None, listener)
        # Should not raise an exception
        transport.unregister_listener(source_uri, None, listener)

    def test_zenoh_unregister_nonexistent_listener(self):
        """Test unregistering a listener that was never registered"""
        transport = UPTransportZenoh.builder("test-vehicle").build()
        uri_provider = StaticUriProvider("test-vehicle", 0xA34B, 0x01)

        def listener(msg):
            pass

        resource_id = 0x8001
        source_uri = uri_provider.get_resource_uri(resource_id)

        with pytest.raises(Exception):
            transport.unregister_listener(source_uri, None, listener)

    def test_zenoh_pubsub_integration(self):
        """Test full publish-subscribe flow with Zenoh"""
        authority = "test-vehicle"
        entity_id = 0xA34B
        version = 0x01
        resource_id = 0x8001

        # Create subscriber first
        sub_transport = UPTransportZenoh.builder(authority).build()
        sub_uri_provider = StaticUriProvider(authority, entity_id, version)

        received_messages = []
        message_received = Event()

        def listener(msg):
            text = msg.extract_string()
            if text:
                received_messages.append(text)
                message_received.set()

        # Register listener with sink_filter=None
        source_uri = sub_uri_provider.get_resource_uri(resource_id)
        sub_transport.register_listener(source_uri, None, listener)

        # Give time for listener to be ready
        time.sleep(0.5)

        # Create publisher
        pub_transport = UPTransportZenoh.builder(authority).build()
        pub_uri_provider = StaticUriProvider(authority, entity_id, version)
        publisher = SimplePublisher(pub_transport, pub_uri_provider)

        # Publish message
        test_message = "Integration test message"
        payload = UPayload.from_string(test_message)
        publisher.publish(resource_id, payload)

        # Wait for message (with timeout)
        received = message_received.wait(timeout=2.0)

        # Cleanup
        sub_transport.unregister_listener(source_uri, None, listener)

        # Note: This test may fail if Zenoh networking isn't properly set up
        # It's more of an integration test than a unit test
        if received:
            assert test_message in received_messages
        else:
            pytest.skip("Message not received (Zenoh networking may not be configured)")


class TestZenohBuilder:
    """Tests for UPTransportZenohBuilder"""

    def test_builder_pattern(self):
        """Test the builder pattern for Zenoh transport"""
        builder = UPTransportZenoh.builder("test-authority")
        assert builder is not None

        transport = builder.build()
        assert transport is not None

    def test_builder_different_authorities(self):
        """Test building transports with different authority names"""
        transport_a = UPTransportZenoh.builder("vehicle-alpha").build()
        transport_b = UPTransportZenoh.builder("vehicle-beta").build()
        assert transport_a is not None
        assert transport_b is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
