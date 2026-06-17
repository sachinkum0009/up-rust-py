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

pub mod communication;
pub mod local_transport;
pub mod uattributes;
pub mod ucode;
pub mod uuid;

#[cfg(feature = "zenoh")]
pub mod zenoh_transport;

use pyo3::prelude::*;

use communication::{RegistrationError, SimpleNotifier, SimplePublisher, UPayload};
use local_transport::{LocalTransport, StaticUriProvider, UMessage, UStatusError};

use crate::{
    local_transport::UUri,
    uattributes::{UAttributes, UMessageType, UPayloadFormat, UPriority},
    ucode::UCode,
    uuid::UUID,
};

#[pymodule]
fn up_rust_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = m.py();
    // version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    // communication submodule
    let communication_mod = PyModule::new(py, "communication")?;
    communication_mod.add_class::<SimplePublisher>()?;
    communication_mod.add_class::<SimpleNotifier>()?;
    communication_mod.add_class::<UPayload>()?;
    communication_mod.add("RegistrationError", py.get_type::<RegistrationError>())?;
    m.add_submodule(&communication_mod)?;

    // local transport submodule
    let local_transport_mod = PyModule::new(py, "local_transport")?;
    local_transport_mod.add_class::<LocalTransport>()?;
    local_transport_mod.add("UStatusError", py.get_type::<UStatusError>())?;
    m.add_submodule(&local_transport_mod)?;

    // Add top-level classes
    m.add_class::<UMessage>()?;
    m.add_class::<StaticUriProvider>()?;
    m.add_class::<UAttributes>()?;
    m.add_class::<UUID>()?;
    m.add_class::<UMessageType>()?;
    m.add_class::<UUri>()?;
    m.add_class::<UPriority>()?;
    m.add_class::<UCode>()?;
    m.add_class::<UPayloadFormat>()?;
    m.add("UStatusError", py.get_type::<UStatusError>())?;
    m.add("RegistrationError", py.get_type::<RegistrationError>())?;

    // Conditionally add zenoh transport submodule
    #[cfg(feature = "zenoh")]
    {
        let zenoh_mod = PyModule::new(py, "zenoh_transport")?;
        zenoh_mod.add_class::<zenoh_transport::UPTransportZenoh>()?;
        zenoh_mod.add_class::<zenoh_transport::UPTransportZenohBuilder>()?;
        m.add_submodule(&zenoh_mod)?;
    }

    Ok(())
}
