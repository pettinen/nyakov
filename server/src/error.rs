use std::fmt;

use poem::{error::ResponseError, http::{header, HeaderValue, StatusCode}, Body, Response};
use serde_json::{json, Value as JsonValue};

enum ResponseComplete {
    True,
}

#[derive(Debug, thiserror::Error)]
#[error("bad-request")]
pub struct BadRequest(String);

impl BadRequest {
    pub fn new(error: &str) -> Self {
        Self(error.to_owned())
    }
}

impl ResponseError for BadRequest {
    fn status(&self) -> StatusCode {
        StatusCode::BAD_REQUEST
    }

    fn as_response(&self) -> Response {
        Response::builder()
            .status(self.status())
            .content_type("application/json")
            .extension(ResponseComplete::True)
            .body(Body::from_json(single_error("general", &self.0, None)).unwrap())
    }
}

#[derive(Debug, thiserror::Error)]
#[error("internal-server-error")]
pub struct InternalError;

impl InternalError {
    pub fn new<E: fmt::Display>(err: E) -> Self {
        tracing::error!("internal error: {}", err);
        InternalError
    }
}

impl ResponseError for InternalError {
    fn status(&self) -> StatusCode {
        StatusCode::INTERNAL_SERVER_ERROR
    }
}

pub async fn error_handler(err: poem::error::Error) -> Response {
    let res = err.as_response();
    if let Some(ResponseComplete::True) = res.data::<ResponseComplete>() {
        return res;
    }

    let (parts, body) = res.into_parts();
    let (mut parts, body) = if parts.status.is_server_error() && !err.is::<InternalError>() {
        InternalError::new(&err).as_response().into_parts()
    } else {
        (parts, body)
    };

    let original_body = match body.into_string().await {
        Ok(body) => body,
        Err(err) => return InternalError::new(err).as_response(),
    };

    let error_id = match parts.status.canonical_reason() {
        Some(reason) => slugify(reason),
        None => return InternalError::new(format!("unexpected status code {}", parts.status)).as_response(),
    };

    let (error_id, details) = if slugify(&original_body) == error_id {
        (error_id, None)
    } else {
        (error_id, Some(original_body))
    };
    parts.headers.insert(
        header::CONTENT_TYPE,
        HeaderValue::from_static("application/json"),
    );
    Response::from_parts(
        parts,
        Body::from_json(single_error("general", &error_id, details)).unwrap(),
    )
}

fn api_alert(source: &str, id: &str, details: Option<String>) -> JsonValue {
    let mut error = json!({ "source": source, "id": id });
    match details {
        Some(details) => {
            error
                .as_object_mut()
                .unwrap()
                .insert("details".to_owned(), JsonValue::String(details));
        }
        None => (),
    }
    error
}

fn single_error(source: &str, id: &str, details: Option<String>) -> JsonValue {
    json!({ "errors": [api_alert(source, id, details)] })
}

fn slugify(value: &str) -> String {
    value.replace(' ', "-").to_lowercase()
}
