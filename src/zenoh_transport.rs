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

//! Zenoh Transport implementation for Python bindings
//!
//! This module provides Python bindings for the up-transport-zenoh-rust implementation,
//! allowing Python applications to use Zenoh as a network transport for uProtocol.

use crate::{communication::get_runtime, local_transport::UUri};

use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::{collections::HashMap, sync::Arc};
use tokio::sync::RwLock;
use up_rust::UUri as RustUUri;
use up_rust::{UListener, UMessage, UTransport};
use up_transport_zenoh::{UPTransportZenoh as RustUPTransportZenoh, zenoh_config};

/// Python wrapper for the Rust UPTransportZenoh
///
/// Provides network transport capabilities using the Zenoh protocol.
/// Unlike LocalTransport which only works within a single process,
/// UPTransportZenoh enables communication across network boundaries.
#[pyclass(name = "UPTransportZenoh")]
pub struct UPTransportZenoh {
    pub(crate) transport: Arc<RustUPTransportZenoh>,
    listeners: Arc<RwLock<HashMap<(RustUUri, Option<RustUUri>), Arc<PythonListener>>>>,
}

#[pymethods]
impl UPTransportZenoh {
    /// Create a new builder for UPTransportZenoh
    ///
    /// Args:
    ///     authority: The authority name (e.g., "my-vehicle", "device-123")
    ///
    /// Returns:
    ///     UPTransportZenohBuilder: A builder instance to configure the transport
    ///
    /// Example:
    ///     ```python
    ///     builder = UPTransportZenoh.builder("my-vehicle")
    ///     transport = builder.build()
    ///     ```
    #[staticmethod]
    fn builder(authority: &str) -> PyResult<UPTransportZenohBuilder> {
        Ok(UPTransportZenohBuilder {
            authority: authority.to_string(),
        })
    }

    /// Send a UMessage via Zenoh transport
    ///
    /// Args:
    ///     message: The UMessage to send
    ///
    /// Returns:
    ///     None
    ///
    /// Raises:
    ///     Exception: If sending fails
    ///
    /// Example:
    ///     ```python
    ///     transport.send(message)
    ///     ```
    fn send(&self, message: crate::local_transport::UMessage) -> PyResult<()> {
        let rust_message = message.inner.clone();
        let transport = self.transport.clone();

        get_runtime()
            .block_on(async move { transport.as_ref().send(rust_message).await })
            .map_err(|e| PyException::new_err(format!("Failed to send message: {e}")))
    }

    /// Register a listener for messages matching the source filter
    ///
    /// Args:
    ///     source_filter: The URI to listen for messages from
    ///     listener: Python callable that receives UMessage objects
    ///
    /// Returns:
    ///     None
    ///
    /// Raises:
    ///     Exception: If registration fails
    ///
    /// Example:
    ///     ```python
    ///     def handle_message(msg):
    ///         print(f"Received: {msg.extract_string()}")
    ///
    ///     transport.register_listener(source_uri, handle_message)
    ///     ```
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
            self.transport
                .register_listener(&source_filter.inner, rust_sink_filter, rust_listener)
                .await
                .map_err(|e| PyException::new_err(format!("Failed to register listener: {e}")))
        })
    }

    /// Unregister a listener for the given source filter
    ///
    /// Args:
    ///     source_filter: The URI to stop listening to
    ///     listener: The Python callable that was registered
    ///
    /// Returns:
    ///     None
    ///
    /// Raises:
    ///     Exception: If unregistration fails
    ///
    /// Note:
    ///     Due to listener instance comparison issues, this may not work as expected.
    ///     Consider letting listeners be cleaned up automatically.
    ///
    /// Example:
    ///     ```python
    ///     transport.unregister_listener(source_uri, handle_message)
    ///     ```
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
                self.transport
                    .unregister_listener(
                        &source_filter.inner,
                        sink_filter.map(|u| &u.inner),
                        rust_listener,
                    )
                    .await
                    .map_err(|e| {
                        PyException::new_err(format!("Failed to unregister listener: {e}"))
                    })
            })
        } else {
            Err(PyException::new_err("Listener not found"))
        }
    }
}

/// Builder for UPTransportZenoh
///
/// Provides a fluent API for configuring and creating a Zenoh transport instance.
#[pyclass(name = "UPTransportZenohBuilder")]
pub struct UPTransportZenohBuilder {
    authority: String,
}

#[pymethods]
impl UPTransportZenohBuilder {
    /// Build the UPTransportZenoh instance
    ///
    /// Returns:
    ///     UPTransportZenoh: The configured transport instance
    ///
    /// Raises:
    ///     Exception: If building fails
    ///
    /// Example:
    ///     ```python
    ///     transport = UPTransportZenoh.builder("my-vehicle").build()
    ///     ```
    fn build(slf: PyRefMut<'_, Self>) -> PyResult<UPTransportZenoh> {
        let authority = slf.authority.clone();

        let transport = get_runtime()
            .block_on(async move {
                RustUPTransportZenoh::builder(&authority)
                    .map_err(|e| format!("Failed to create builder: {e}"))?
                    .with_config(zenoh_config::Config::default())
                    .build()
                    .await
                    .map_err(|e| format!("Failed to build transport: {e}"))
            })
            .map_err(|e: String| PyException::new_err(e))?;

        Ok(UPTransportZenoh {
            transport: Arc::new(transport),
            listeners: Arc::new(RwLock::new(HashMap::new())),
        })
    }
}

/// Bridges Python callable to Rust UListener trait
struct PythonListener {
    callback: PyObject,
}

#[async_trait::async_trait]
impl UListener for PythonListener {
    async fn on_receive(&self, msg: UMessage) {
        Python::with_gil(|py| {
            let py_msg = crate::local_transport::UMessage { inner: msg };

            if let Err(e) = self.callback.call1(py, (py_msg,)) {
                eprintln!("Error calling Python Zenoh listener: {:?}", e);
            }
        });
    }
}
