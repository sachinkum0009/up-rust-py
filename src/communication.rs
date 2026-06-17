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

use up_rust::UPayloadFormat;
use up_rust::communication::{
    CallOptions, Notifier, Publisher, RegistrationError as RustRegistrationError,
    SimpleNotifier as RustSimpleNotifier, SimplePublisher as RustSimplePublisher,
    UPayload as RustUPayload,
};
use up_rust::{
    StaticUriProvider as RustStaticUriProvider, UListener, UMessage as RustUMessage, UTransport,
    local_transport::LocalTransport as RustLocalTransport,
};

use protobuf::well_known_types::wrappers::StringValue;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::PyAny;
use std::collections::HashMap;
use std::sync::{Arc, Mutex, OnceLock};
use tokio::runtime::Runtime;

use crate::local_transport::{LocalTransport, StaticUriProvider, UUri};

static RUNTIME: OnceLock<Runtime> = OnceLock::new();

pub fn get_runtime() -> &'static Runtime {
    RUNTIME.get_or_init(|| {
        tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("Failed to create Tokio runtime")
    })
}

#[cfg(feature = "zenoh")]
use crate::zenoh_transport::UPTransportZenoh;

create_exception!(up_rust_py, RegistrationError, PyException);

/// Enum to hold different transport types
enum TransportType {
    Local(Arc<RustLocalTransport>),
    #[cfg(feature = "zenoh")]
    Zenoh(Arc<up_transport_zenoh::UPTransportZenoh>),
}

impl TransportType {
    #[allow(dead_code)]
    fn as_transport(&self) -> &dyn UTransport {
        match self {
            TransportType::Local(t) => t.as_ref(),
            #[cfg(feature = "zenoh")]
            TransportType::Zenoh(t) => t.as_ref(),
        }
    }
    fn as_transport_arc(&self) -> Arc<dyn UTransport> {
        match self {
            TransportType::Local(t) => t.clone() as Arc<dyn UTransport>,
            #[cfg(feature = "zenoh")]
            TransportType::Zenoh(t) => t.clone() as Arc<dyn UTransport>,
        }
    }
}

/// Represents a message payload in uProtocol.
///
/// UPayload encapsulates the data being transmitted in a uProtocol message.
/// It can be created from strings or raw bytes.
#[pyclass]
#[derive(Clone)]
pub struct UPayload {
    inner: RustUPayload,
}

#[pymethods]
impl UPayload {
    /// Create a UPayload from a string value.
    ///
    /// Args:
    ///     value (str): The string content to wrap in the payload.
    ///
    /// Returns:
    ///     UPayload: A new payload instance containing the string.
    ///
    /// Raises:
    ///     Exception: If the payload creation fails.
    ///
    /// Example:
    ///     >>> payload = up_rust_py.UPayload.from_string("Hello, World!")
    #[staticmethod]
    fn from_string(value: String) -> PyResult<Self> {
        let string_value = StringValue {
            value,
            ..Default::default()
        };
        let payload = RustUPayload::try_from_protobuf(string_value)
            .map_err(|e| PyException::new_err(format!("Failed to create payload: {}", e)))?;
        Ok(UPayload { inner: payload })
    }

    /// Create a UPayload from raw bytes.
    ///
    /// Args:
    ///     data (list[int]): A list of bytes (0-255) to wrap in the payload.
    ///
    /// Returns:
    ///     UPayload: A new payload instance containing the binary data.
    ///
    /// Example:
    ///     >>> payload = up_rust_py.UPayload.from_bytes([72, 101, 108, 108, 111])
    #[staticmethod]
    fn from_bytes(data: Vec<u8>) -> PyResult<Self> {
        // Create a simple bytes payload with a generic format
        Ok(UPayload {
            inner: RustUPayload::new(
                data,
                UPayloadFormat::UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            ),
        })
    }
}

/// Publisher for sending uProtocol messages.
///
/// SimplePublisher provides an easy-to-use interface for publishing messages
/// to specific resources in the uProtocol network. It works with any transport
/// implementation (LocalTransport, UPTransportZenoh, etc.).
#[pyclass]
pub struct SimplePublisher {
    transport: TransportType,
    uri_provider: Arc<RustStaticUriProvider>,
}

#[pymethods]
impl SimplePublisher {
    /// Create a new SimplePublisher with LocalTransport.
    ///
    /// Args:
    ///     transport (LocalTransport): The local transport to use for sending messages.
    ///     uri_provider (StaticUriProvider): The URI provider for the publishing entity.
    ///
    /// Returns:
    ///     SimplePublisher: A new publisher instance.
    ///
    /// Raises:
    ///     Exception: If the runtime creation fails.
    ///
    /// Example:
    ///     >>> transport = up_rust_py.LocalTransport()
    ///     >>> provider = up_rust_py.StaticUriProvider("device", 0x1234, 0x01)
    ///     >>> publisher = up_rust_py.SimplePublisher(transport, provider)
    #[new]
    fn new(transport: Bound<'_, PyAny>, uri_provider: &StaticUriProvider) -> PyResult<Self> {
        // Use 'downcast' or 'extract' on the Bound object
        let transport_type =
            if let Ok(local_transport) = transport.extract::<PyRef<LocalTransport>>() {
                TransportType::Local(local_transport.inner.clone())
            } else {
                #[cfg(feature = "zenoh")]
                if let Ok(zenoh_transport) = transport.extract::<PyRef<UPTransportZenoh>>() {
                    TransportType::Zenoh(zenoh_transport.transport.clone())
                } else {
                    return Err(PyException::new_err(
                        "Transport must be LocalTransport or UPTransportZenoh",
                    ));
                }
                #[cfg(not(feature = "zenoh"))]
                return Err(PyException::new_err("Transport must be LocalTransport"));
            };

        Ok(SimplePublisher {
            transport: transport_type,
            uri_provider: uri_provider.inner.clone(),
        })
    }

    /// Publish a message to a specific resource.
    ///
    /// Args:
    ///     resource_id (int): The target resource ID (0 to 65535).
    ///     payload (UPayload | None): The message payload, or None for empty messages.
    ///
    /// Raises:
    ///     Exception: If publishing fails.
    ///
    /// Example:
    ///     >>> payload = up_rust_py.UPayload.from_string("Hello")
    ///     >>> publisher.publish(0xb4c1, payload)
    ///     >>> # Or publish without payload:
    ///     >>> publisher.publish(0xb4c1, None)
    #[pyo3(signature = (resource_id, payload=None))]
    fn publish(&mut self, resource_id: u16, payload: Option<UPayload>) -> PyResult<()> {
        let payload_inner = payload.map(|p| p.inner);
        let call_options = CallOptions::for_publish(None, None, None);
        let transport_arc = self.transport.as_transport_arc();
        let uri_provider = self.uri_provider.clone();

        get_runtime().block_on(async move {
            let publisher = RustSimplePublisher::new(transport_arc, uri_provider);
            publisher
                .publish(resource_id, call_options, payload_inner)
                .await
                .map_err(|e| PyException::new_err(format!("Failed to publish: {}", e)))
        })
    }
}

/// Internal struct to bridge Python callbacks to Rust UListener trait for notifications
struct PythonNotificationListener {
    callback: PyObject,
}

#[async_trait::async_trait]
impl UListener for PythonNotificationListener {
    async fn on_receive(&self, msg: RustUMessage) {
        Python::with_gil(|py| {
            let py_msg = crate::local_transport::UMessage { inner: msg };
            if let Err(e) = self.callback.call1(py, (py_msg,)) {
                eprintln!("Error calling Python notification callback: {:?}", e);
            }
        });
    }
}

fn map_registration_error(context: &str, err: RustRegistrationError) -> PyErr {
    match err {
        RustRegistrationError::AlreadyExists => {
            let full_message = format!(
                "{}: a listener for the given filter criteria already exists",
                context
            );
            Python::with_gil(|py| {
                let py_err = PyErr::new::<RegistrationError, _>(full_message);
                let err_value = py_err.value(py);
                let _ = err_value.setattr("kind", "ALREADY_EXISTS");
                let _ = err_value.setattr("message", "listener already registered for filters");
                py_err
            })
        }
        RustRegistrationError::NoSuchListener => {
            let full_message = format!("{}: no listener registered for given pattern", context);
            Python::with_gil(|py| {
                let py_err = PyErr::new::<RegistrationError, _>(full_message);
                let err_value = py_err.value(py);
                let _ = err_value.setattr("kind", "NOT_FOUND");
                let _ = err_value.setattr("message", "no listener registered for given pattern");
                py_err
            })
        }
        RustRegistrationError::MaxListenersExceeded => {
            let full_message = format!("{}: maximum number of listeners has been reached", context);
            Python::with_gil(|py| {
                let py_err = PyErr::new::<RegistrationError, _>(full_message);
                let err_value = py_err.value(py);
                let _ = err_value.setattr("kind", "RESOURCE_EXHAUSTED");
                let _ =
                    err_value.setattr("message", "maximum number of listeners has been reached");
                py_err
            })
        }
        RustRegistrationError::PushDeliveryMethodNotSupported => {
            let full_message = format!(
                "{}: the underlying transport implementation does not support the push delivery method",
                context
            );
            Python::with_gil(|py| {
                let py_err = PyErr::new::<RegistrationError, _>(full_message);
                let err_value = py_err.value(py);
                let _ = err_value.setattr("kind", "UNIMPLEMENTED");
                let _ = err_value.setattr(
                    "message",
                    "the underlying transport implementation does not support the push delivery method",
                );
                py_err
            })
        }
        RustRegistrationError::InvalidFilter(msg) => {
            let full_message = format!("{}: invalid filter(s): {}", context, msg);
            Python::with_gil(|py| {
                let py_err = PyErr::new::<RegistrationError, _>(full_message);
                let err_value = py_err.value(py);
                let _ = err_value.setattr("kind", "INVALID_FILTER");
                let _ = err_value.setattr("message", msg.clone());
                py_err
            })
        }
        RustRegistrationError::Unknown(status) => {
            let code = status.get_code();
            let code_name = format!("{:?}", code);
            let status_message = status.get_message();
            let full_message = format!("{}: {} (code={})", context, status_message, code_name);
            Python::with_gil(|py| {
                let py_err = PyErr::new::<RegistrationError, _>(full_message);
                let err_value = py_err.value(py);
                let _ = err_value.setattr("kind", "UNKNOWN");
                let _ = err_value.setattr("code", code_name.clone());
                let _ = err_value.setattr("message", status_message.clone());
                py_err
            })
        }
    }
}

/// A Notifier that uses the uProtocol Transport Layer API to send and receive notifications to/from (other) uEntities.
///
/// SimpleNotifier provides an easy-to-use interface for sending notifications
/// and listening for notifications from other entities in the uProtocol network.
#[pyclass]
pub struct SimpleNotifier {
    inner: RustSimpleNotifier,
    // Store listeners to enable proper unregistration
    // Key is a string representation of the topic URI
    listeners: Arc<Mutex<HashMap<String, Arc<PythonNotificationListener>>>>,
}

#[pymethods]
impl SimpleNotifier {
    /// Create a new SimpleNotifier.
    ///
    /// Args:
    ///     transport (LocalTransport): The transport to use for sending and receiving notifications.
    ///     uri_provider (StaticUriProvider): The URI provider for the notifying entity.
    ///
    /// Returns:
    ///     SimpleNotifier: A new notifier instance.
    ///
    /// Raises:
    ///     Exception: If the runtime creation fails.
    ///
    /// Example:
    ///     >>> transport = up_rust_py.LocalTransport()
    ///     >>> provider = up_rust_py.StaticUriProvider("my-vehicle", 0xa34b, 0x01)
    ///     >>> notifier = up_rust_py.SimpleNotifier(transport, provider)
    #[new]
    fn new(transport: &LocalTransport, uri_provider: &StaticUriProvider) -> PyResult<Self> {
        Ok(SimpleNotifier {
            inner: RustSimpleNotifier::new(transport.inner.clone(), uri_provider.inner.clone()),
            listeners: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    /// Start listening for notifications on a specific topic.
    ///
    /// Args:
    ///     topic (UUri): The topic URI to listen to.
    ///     callback (callable): A Python function that accepts a UMessage parameter.
    ///                         Will be called when notifications arrive.
    ///
    /// Raises:
    ///     RegistrationError: If listener registration fails.
    ///
    /// Example:
    ///     >>> def notification_handler(msg: UMessage):
    ///     ...     text = msg.extract_string()
    ///     ...     if text:
    ///     ...         print(f"Notification: {text}")
    ///     >>> topic = uri_provider.get_resource_uri(0xd100)
    ///     >>> notifier.start_listening(topic, notification_handler)
    fn start_listening(
        &mut self,
        py: Python<'_>,
        topic: &UUri,
        callback: PyObject,
    ) -> PyResult<()> {
        let topic_key = format!("{:?}", topic.inner);

        let listener = Arc::new(PythonNotificationListener {
            callback: callback.clone_ref(py),
        });

        get_runtime().block_on(async {
            self.inner
                .start_listening(&topic.inner, listener.clone())
                .await
                .map_err(|e| map_registration_error("Failed to start listening", e))
        })?;

        // Store the listener only after successful transport registration.
        {
            let mut listeners = self.listeners.lock().map_err(|e| {
                PyException::new_err(format!("Failed to acquire listener lock: {}", e))
            })?;
            listeners.insert(topic_key, listener.clone());
        }

        Ok(())
    }

    /// Stop listening for notifications on a specific topic.
    ///
    /// Args:
    ///     topic (UUri): The topic URI to stop listening to.
    ///     callback (callable): The same Python function that was registered.
    ///
    /// Raises:
    ///     RegistrationError: If listener unregistration fails.
    ///
    /// Example:
    ///     >>> notifier.stop_listening(topic, notification_handler)
    fn stop_listening(&mut self, _py: Python, topic: &UUri, _callback: PyObject) -> PyResult<()> {
        // Create the same key used during registration
        let topic_key = format!("{:?}", topic.inner);

        // Retrieve the stored listener without removing it yet.
        let listener = {
            let listeners = self.listeners.lock().map_err(|e| {
                PyException::new_err(format!("Failed to acquire listener lock: {}", e))
            })?;
            listeners.get(&topic_key).cloned().ok_or_else(|| {
                PyException::new_err(format!("No listener registered for topic: {}", topic_key))
            })?
        };

        get_runtime().block_on(async {
            self.inner
                .stop_listening(&topic.inner, listener)
                .await
                .map_err(|e| map_registration_error("Failed to stop listening", e))
        })?;

        // Remove listener from local map only after successful transport unregistration.
        {
            let mut listeners = self.listeners.lock().map_err(|e| {
                PyException::new_err(format!("Failed to acquire listener lock: {}", e))
            })?;
            listeners.remove(&topic_key);
        }

        Ok(())
    }

    /// Send a notification to a specific destination.
    ///
    /// Args:
    ///     resource_id (int): The notification resource ID (0 to 65535).
    ///     destination (UUri): The destination URI to send the notification to.
    ///     payload (UPayload | None): The notification payload, or None for empty notifications.
    ///
    /// Raises:
    ///     Exception: If notification sending fails.
    ///
    /// Example:
    ///     >>> payload = up_rust_py.UPayload.from_string("Alert!")
    ///     >>> destination = uri_provider.get_source_uri()
    ///     >>> notifier.notify(0xd100, destination, payload)
    #[pyo3(signature = (resource_id, destination, payload=None))]
    fn notify(
        &mut self,
        resource_id: u16,
        destination: &UUri,
        payload: Option<UPayload>,
    ) -> PyResult<()> {
        let payload_inner = payload.map(|p| p.inner);
        let call_options = CallOptions::for_notification(None, None, None);

        get_runtime().block_on(async {
            self.inner
                .notify(resource_id, &destination.inner, call_options, payload_inner)
                .await
                .map_err(|e| PyException::new_err(format!("Failed to send notification: {}", e)))
        })
    }
}
