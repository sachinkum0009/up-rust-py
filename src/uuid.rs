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

use pyo3::prelude::*;
use up_rust::UUID as RustUUID;

#[pyclass(name = "UUID")]
#[derive(Clone)]
pub struct UUID {
    pub(crate) inner: RustUUID,
}

#[pymethods]
impl UUID {
    fn get_msb(&self) -> u64 {
        self.inner.msb
    }

    fn get_lsb(&self) -> u64 {
        self.inner.lsb
    }
}
