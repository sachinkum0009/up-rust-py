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

from up_rust_py import StaticUriProvider
from up_rust_py.communication import SimplePublisher, UPayload
from up_rust_py.local_transport import LocalTransport


class TestSimplePublisher:
    """Tests SimplePublisher"""

    def test_create_publisher(self):
        """Test creating SimplePublisher instance"""
        uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
        transport = LocalTransport()

        publisher = SimplePublisher(transport, uri_provider)

        assert publisher is not None
        assert hasattr(publisher, "publish")

    def test_publisher_with_string_payload(self):
        """Test publishing with string payload"""
        uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
        transport = LocalTransport()
        publisher = SimplePublisher(transport, uri_provider)

        payload = UPayload.from_string("Test message")
        # Should not raise exception
        publisher.publish(0x8001, payload)

    def test_publisher_with_bytes_payload(self):
        """Test publishing with bytes payload"""
        uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
        transport = LocalTransport()
        publisher = SimplePublisher(transport, uri_provider)

        payload = UPayload.from_bytes([0x01, 0x02, 0x03, 0x04])
        # Should not raise exception
        publisher.publish(0x8001, payload)

    def test_publisher_with_none_payload(self):
        """Test publishing without payload"""
        uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
        transport = LocalTransport()
        publisher = SimplePublisher(transport, uri_provider)

        # Should not raise exception
        publisher.publish(0x8001, None)

    def test_publisher_multiple_messages(self):
        """Test publishing multiple messages"""
        uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
        transport = LocalTransport()
        publisher = SimplePublisher(transport, uri_provider)

        # Publish multiple messages - should not raise exception
        for i in range(5):
            payload = UPayload.from_string(f"Message {i}")
            publisher.publish(0x8001, payload)

    def test_publisher_different_resource_ids(self):
        """Test publishing to different resource IDs"""
        uri_provider = StaticUriProvider("my-vehicle", 0xA34B, 0x01)
        transport = LocalTransport()
        publisher = SimplePublisher(transport, uri_provider)

        payload = UPayload.from_string("Test")

        # Publish to different resource IDs
        for resource_id in [0x8001, 0x8002, 0x8003]:
            publisher.publish(resource_id, payload)


class TestUPayload:
    """Tests for UPayload"""

    def test_payload_from_string(self):
        """Test creating payload from string"""
        payload = UPayload.from_string("Hello World")
        assert payload is not None

    def test_payload_from_bytes(self):
        """Test creating payload from bytes"""
        payload = UPayload.from_bytes([0x48, 0x65, 0x6C, 0x6C, 0x6F])
        assert payload is not None

    def test_payload_from_empty_string(self):
        """Test creating payload from empty string"""
        payload = UPayload.from_string("")
        assert payload is not None

    def test_payload_from_empty_bytes(self):
        """Test creating payload from empty bytes"""
        payload = UPayload.from_bytes([])
        assert payload is not None


class TestStaticUriProvider:
    """Tests for StaticUriProvider"""

    def test_create_uri_provider(self):
        """Test creating URI provider"""
        provider = StaticUriProvider("test-vehicle", 0x1234, 0x01)
        assert provider is not None

    def test_get_resource_uri(self):
        """Test getting resource URI"""
        provider = StaticUriProvider("test-vehicle", 0x1234, 0x01)
        uri = provider.get_resource_uri(0x8001)
        assert uri is not None

    def test_get_source_uri(self):
        """Test getting source URI"""
        provider = StaticUriProvider("test-vehicle", 0x1234, 0x01)
        uri = provider.get_source_uri()
        assert uri is not None


class TestLocalTransport:
    """Tests for LocalTransport"""

    def test_create_transport(self):
        """Test creating LocalTransport"""
        transport = LocalTransport()
        assert transport is not None

    def test_register_listener(self):
        """Test registering a listener"""
        transport = LocalTransport()
        provider = StaticUriProvider("test-vehicle", 0x1234, 0x01)
        resource_id = 0x8001
        uuri = provider.get_resource_uri(resource_id)

        def listener(msg):
            pass

        # Should not raise exception
        transport.register_listener(uuri, None, listener)

    def test_unregister_listener(self):
        """Test unregistering a listener"""
        transport = LocalTransport()
        provider = StaticUriProvider("test-vehicle", 0x1234, 0x01)
        resource_id = 0x8001
        uuri = provider.get_resource_uri(resource_id)

        def listener(msg):
            pass

        transport.register_listener(uuri, None, listener)
        # This should also not raise exception
        transport.unregister_listener(uuri, None, listener)


def test_version():
    """Test that the version is accessible"""
    import up_rust_py

    assert hasattr(up_rust_py, "__version__")
    assert up_rust_py.__version__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
