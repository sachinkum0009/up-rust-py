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
use up_rust::UAttributes as RustUAttributes;
use up_rust::UMessageType as RustUMessageType;
use up_rust::UPayloadFormat as RustUPayloadFormat;
use up_rust::UPriority as RustUPriority;

use crate::local_transport::UUri;
use crate::ucode::UCode;
use crate::uuid::UUID;

/// UAttributes class
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct UAttributes {
    pub(crate) inner: RustUAttributes,
}

#[pymethods]
impl UAttributes {
    fn get_id(&self) -> Option<UUID> {
        self.inner.id.as_ref().map(|rust_uuid| UUID {
            inner: rust_uuid.clone(),
        })
    }

    fn get_type_(&self) -> Option<UMessageType> {
        self.inner
            .type_
            .enum_value()
            .ok()
            .map(|rust_type_| UMessageType { inner: rust_type_ })
    }

    fn get_source(&self) -> Option<UUri> {
        self.inner.source.as_ref().map(|rust_source| UUri {
            inner: rust_source.clone(),
        })
    }

    fn get_sink(&self) -> Option<UUri> {
        self.inner.sink.as_ref().map(|rust_sink| UUri {
            inner: rust_sink.clone(),
        })
    }

    fn get_priority(&self) -> Option<UPriority> {
        self.inner
            .priority
            .enum_value()
            .ok()
            .map(|rust_priority| UPriority {
                inner: rust_priority,
            })
    }

    fn get_ttl(&self) -> Option<u32> {
        self.inner.ttl
    }

    fn get_permission_level(&self) -> Option<u32> {
        self.inner.permission_level
    }

    fn get_commstatus(&self) -> Option<UCode> {
        self.inner
            .commstatus
            .unwrap()
            .enum_value()
            .ok()
            .map(|rust_commstatus| UCode {
                inner: rust_commstatus,
            })
    }

    fn get_reqid(&self) -> Option<UUID> {
        self.inner.reqid.as_ref().map(|rust_reqid| UUID {
            inner: rust_reqid.clone(),
        })
    }

    fn get_token(&self) -> Option<String> {
        self.inner.token.clone()
    }

    fn get_traceparent(&self) -> Option<String> {
        self.inner.traceparent.clone()
    }

    fn get_payload_format(&self) -> Option<UPayloadFormat> {
        self.inner
            .payload_format
            .enum_value()
            .ok()
            .map(|rust_payload_format| UPayloadFormat {
                inner: rust_payload_format,
            })
    }
}

#[pyclass(from_py_object, name = "UMessageType")]
#[derive(Clone)]
pub struct UMessageType {
    #[expect(dead_code)]
    pub(crate) inner: RustUMessageType,
}

// TODO(Sachin): Handle the parsing of enum
// impl UMessageType {
//     fn get_enum(&self) {
//         let my_enum = self.inner;
//         match my_enum {
//             RustUMessageType::UMESSAGE_TYPE_NOTIFICATION
//         }
//     }
// }

#[pyclass(from_py_object, name = "UPriority")]
#[derive(Clone)]
pub struct UPriority {
    #[expect(dead_code)]
    pub(crate) inner: RustUPriority,
}

// TODO(Sachin): Handle the parsing of enum
impl UPriority {}

#[pyclass(from_py_object, name = "UPayloadFormat")]
#[derive(Clone)]
pub struct UPayloadFormat {
    #[expect(dead_code)]
    pub(crate) inner: RustUPayloadFormat,
}

// TODO(Sachin): Handle the parsing of enum
impl UPayloadFormat {}
