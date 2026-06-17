/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

use crate::communication::get_runtime;
use crate::uattributes::UAttributes;

use tokio::sync::RwLock;
use up_rust::UUri as RustUUri;
use up_rust::{
    LocalUriProvider, StaticUriProvider as RustStaticUriProvider, UListener as RustUListener,
    UMessage as RustUMessage, UTransport, local_transport::LocalTransport as RustLocalTransport,
};

use protobuf::well_known_types::wrappers::StringValue;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::hash::Hash;
use std::sync::Arc;

create_exception!(up_rust_py, UStatusError, PyException);

fn map_ustatus_error(context: &str, status: up_rust::UStatus) -> PyErr {
    let code = status.get_code();
    let code_name = format!("{:?}", code);
    let status_message = status.get_message();
    let full_message = format!("{}: {} (code={})", context, status_message, code_name);

    Python::with_gil(|py| {
        let err = PyErr::new::<UStatusError, _>(full_message);
        let err_value = err.value(py);
        let _ = err_value.setattr("code", code_name.clone());
        let _ = err_value.setattr("message", status_message.clone());
        err
    })
}

/// Internal struct to bridge Python callbacks to Rust UListener trait
struct PythonListener {
    callback: PyObject,
}

#[async_trait::async_trait]
impl RustUListener for PythonListener {
    async fn on_receive(&self, msg: RustUMessage) {
        Python::with_gil(|py| {
            let py_msg = crate::local_transport::UMessage { inner: msg };

            if let Err(e) = self.callback.call1(py, (py_msg,)) {
                eprintln!("Error calling Python listener: {:?}", e);
            }
        });
    }
}

/// Represents a complete uProtocol message.
///
/// UMessage encapsulates both the payload and metadata for a uProtocol communication.
/// It is typically received by listener callbacks.
#[pyclass]
#[derive(Clone)]
pub struct UMessage {
    pub(crate) inner: RustUMessage,
}

#[pymethods]
impl UMessage {
    /// Get the message attributes.
    fn get_attributes(&self) -> Option<UAttributes> {
        self.inner.attributes.as_ref().map(|attr| UAttributes {
            inner: attr.clone(),
        })
    }
    /// Get the raw payload bytes.
    ///
    /// Returns:
    ///     bytes | None: The raw payload, or None if the message has no payload.
    fn get_payload(&self) -> Option<Vec<u8>> {
        self.inner.payload.clone().map(|b| b.to_vec())
    }

    /// Extract a string value from the message payload.
    ///
    /// Returns:
    ///     str | None: The extracted string if the payload is a protobuf StringValue,
    ///                 otherwise None.
    fn extract_string(&self) -> PyResult<Option<String>> {
        match self.inner.extract_protobuf::<StringValue>() {
            Ok(value) => Ok(Some(value.value)),
            Err(_) => Ok(None),
        }
    }

    fn __repr__(&self) -> String {
        let has_payload = self.inner.payload.is_some();
        let type_str = self
            .inner
            .type_()
            .map(|t| format!("{:?}", t))
            .unwrap_or_default();
        format!("UMessage(type={}, payload={})", type_str, has_payload)
    }
}

/// UUri class
#[pyclass]
#[derive(Clone, Hash, PartialEq, Eq)]
pub struct UUri {
    pub inner: RustUUri,
}

/// Provides URI information for uProtocol entities.
///
/// StaticUriProvider creates and manages URIs for identifying entities
/// in the uProtocol network. It combines an authority (device/vehicle name),
/// entity ID, and version to create unique identifiers.
#[pyclass]
pub struct StaticUriProvider {
    pub(crate) inner: Arc<RustStaticUriProvider>,
}

#[pymethods]
impl StaticUriProvider {
    /// Create a new StaticUriProvider.
    ///
    /// Args:
    ///     authority (str): The authority name identifying the device/vehicle
    ///                     (e.g., "my-vehicle", "sensor-001").
    ///     entity_id (int): The entity ID (0 to 2^32-1, e.g., 0xa34b).
    ///     version (int): The version number (0 to 255, e.g., 0x01).
    ///
    /// Returns:
    ///     StaticUriProvider: A new URI provider instance.
    ///
    /// Example:
    ///     >>> provider = up_rust_py.StaticUriProvider("my-vehicle", 0xa34b, 0x01)
    #[new]
    fn new(authority: String, entity_id: u32, version: u8) -> Self {
        StaticUriProvider {
            inner: Arc::new(RustStaticUriProvider::new(&authority, entity_id, version)),
        }
    }

    fn get_resource_uri(&self, _py: Python, resource_id: u16) -> UUri {
        let uuri = self.inner.get_resource_uri(resource_id);
        UUri { inner: uuri }
    }

    /// Get the source URI for this entity.
    ///
    /// Returns:
    ///     UUri: The source URI identifying this entity.
    ///
    /// Example:
    ///     >>> provider = up_rust_py.StaticUriProvider("my-vehicle", 0xa34b, 0x01)
    ///     >>> source_uri = provider.get_source_uri()
    fn get_source_uri(&self, _py: Python) -> UUri {
        let uuri = self.inner.get_source_uri();
        UUri { inner: uuri }
    }
}

/// Provides local (in-process) transport for uProtocol communication.
///
/// LocalTransport enables communication between components within the same
/// process without network overhead. It manages listener registration and
/// message routing.
#[pyclass]
pub struct LocalTransport {
    pub(crate) inner: Arc<RustLocalTransport>,
    listeners: Arc<RwLock<HashMap<(RustUUri, Option<RustUUri>), Arc<PythonListener>>>>,
}

#[pymethods]
impl LocalTransport {
    /// Create a new LocalTransport instance.
    ///
    /// Returns:
    ///     LocalTransport: A new transport instance.
    ///
    /// Raises:
    ///     Exception: If the runtime creation fails.
    ///
    /// Example:
    ///     >>> transport = up_rust_py.LocalTransport()
    #[new]
    fn new() -> PyResult<Self> {
        Ok(LocalTransport {
            inner: Arc::new(RustLocalTransport::default()),
            listeners: Arc::new(RwLock::new(HashMap::new())),
        })
    }

    /// Registers a listener to be called for messages.
    ///
    /// The listener will be invoked for each message that matches the given source and sink filter patterns
    /// according to the rules defined by the [UUri specification](https://github.com/eclipse-uprotocol/up-spec/blob/v1.6.0-alpha.7/basics/uri.adoc).
    ///
    /// # Arguments
    ///
    /// * `source_filter` - The _source_ address pattern that messages need to match.
    /// * `sink_filter` - The _sink_ address pattern that messages need to match,
    ///                   or `None` to match messages that do not contain any sink address.
    ///
    /// # Raises:
    ///     UStatusError: If the listener could not be registered.
    ///
    /// # Example:
    ///     >>> def my_handler(msg: UMessage):
    ///     ...     print(msg)
    ///     >>> transport.register_listener(source_pattern, sink_pattern, my_handler)
    #[pyo3(signature = (source_filter, sink_filter, listener))]
    fn register_listener(
        &mut self,
        py: Python<'_>,
        source_filter: &UUri,
        sink_filter: Option<&UUri>,
        listener: PyObject,
    ) -> PyResult<()> {
        let rust_listener = Arc::new(PythonListener {
            callback: listener.clone_ref(py),
        });
        let key = (
            source_filter.inner.clone(),
            sink_filter.map(|u| u.inner.clone()),
        );
        self.listeners
            .blocking_write()
            .insert(key, rust_listener.clone());
        let rust_sink_filter = sink_filter.map(|uuri| &uuri.inner);

        get_runtime().block_on(async {
            self.inner
                .register_listener(&source_filter.inner, rust_sink_filter, rust_listener)
                .await
                .map_err(|e| map_ustatus_error("Failed to register listener", e))
        })
    }

    /// Deregisters a message listener.
    ///
    /// The listener will no longer be called for any (matching) messages after this function has
    /// returned successfully.
    ///
    /// This default implementation returns an error with [`UCode::UNIMPLEMENTED`].
    ///
    /// # Arguments
    ///
    /// * `source_filter` - The _source_ address pattern that the listener had been registered for.
    /// * `sink_filter` - The _sink_ address pattern that the listener had been registered for.
    /// * `listener` - The listener to unregister.
    ///
    /// # Errors
    ///
    /// Returns an error if the listener could not be unregistered, for example if the given listener does not exist.
    #[pyo3(signature = (source_filter, sink_filter, listener))]
    fn unregister_listener(
        &mut self,
        py: Python<'_>,
        source_filter: &UUri,
        sink_filter: Option<&UUri>,
        listener: PyObject,
    ) -> PyResult<()> {
        let _ = (py, listener);
        let key = (
            source_filter.inner.clone(),
            sink_filter.map(|u| u.inner.clone()),
        );
        if let Some(rust_listener) = self.listeners.blocking_write().remove(&key) {
            get_runtime().block_on(async {
                self.inner
                    .unregister_listener(
                        &source_filter.inner,
                        sink_filter.map(|u| &u.inner),
                        rust_listener,
                    )
                    .await
                    .map_err(|e| map_ustatus_error("Failed to unregister listener", e))
            })
        } else {
            Err(PyErr::new::<UStatusError, _>("Listener not found"))
        }
    }
}
