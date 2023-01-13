use std::{
    collections::{HashMap, HashSet},
    fs::File,
    io::{BufRead, BufReader},
    ops::Deref,
    path::PathBuf,
    sync::Mutex,
};

use chrono::NaiveDate;
use lazy_static::lazy_static;
use poem::{handler, web::Query, Body, Endpoint, EndpointExt, Response, Route};
use rand::{thread_rng, Rng};
use regex::Regex;
use serde::{ser::SerializeMap, Deserialize, Serialize, Serializer};
use serde_json::json;
use tracing::warn;

mod emotes;
mod error;

use emotes::{BTTV_EMOTES, TWITCH_EMOTES};
use error::{error_handler, BadRequest, InternalError};

const MIN_MESSAGE_WORDS: usize = 0;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Metadata {
    lines: usize,
    log_files: usize,
    first: NaiveDate,
    last: NaiveDate,
}

struct CountMap {
    counts: HashMap<String, usize>,
    total: usize,
}

impl CountMap {
    fn new() -> Self {
        Self {
            counts: HashMap::new(),
            total: 0,
        }
    }

    fn new_with_item(item: String) -> Self {
        Self {
            counts: HashMap::from([(item, 1)]),
            total: 1,
        }
    }
}

lazy_static! {
    static ref ALTERNATIVES: Mutex<HashMap<String, CountMap>> = Mutex::new(HashMap::new());
    static ref FIRST_WORDS: Mutex<HashMap<String, CountMap>> = Mutex::new(HashMap::new());
    static ref METADATA: Mutex<HashMap<String, Metadata>> = Mutex::new(HashMap::new());
    static ref USERNAMES: Mutex<CountMap> = Mutex::new(CountMap::new());
    static ref TIMESTAMPS: Mutex<HashMap<String, CountMap>> = Mutex::new(HashMap::new());
    static ref WORD_MAP: Mutex<HashMap<String, CountMap>> = Mutex::new(HashMap::new());
    static ref NORMALIZE_RE: Regex = Regex::new(r#"[-';!?_@,."']"#).unwrap();
}

struct Emote {
    id: String,
    name: String,
    source: String,
}

enum Word {
    Emote(Emote),
    Text(String),
}

impl Serialize for Word {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        let len = match self {
            Self::Emote(_) => 4,
            Self::Text(_) => 2,
        };
        let mut map = serializer.serialize_map(Some(len))?;
        match self {
            Self::Emote(emote) => {
                map.serialize_entry("id", &emote.id)?;
                map.serialize_entry("name", &emote.name)?;
                map.serialize_entry("source", &emote.source)?;
                map.serialize_entry("type", "emote")?;
            }
            Self::Text(text) => {
                map.serialize_entry("text", text)?;
                map.serialize_entry("type", "text")?;
            }
        }
        map.end()
    }
}

#[derive(Deserialize)]
struct GenerateQuoteParams {
    user: Option<String>,
}

#[handler]
async fn generate_quote(
    Query(GenerateQuoteParams { user }): Query<GenerateQuoteParams>,
) -> poem::Result<Response> {
    let alternatives = ALTERNATIVES.lock().unwrap();
    let first_words = FIRST_WORDS.lock().unwrap();
    let timestamps = TIMESTAMPS.lock().unwrap();
    let usernames = USERNAMES.lock().unwrap();
    let word_map = WORD_MAP.lock().unwrap();

    let username = match user {
        Some(username) => {
            let username = username.to_lowercase();
            if !usernames.counts.contains_key(&username) {
                Err(BadRequest::new("user-not-found"))?;
            }
            username
        }
        None => weighted_random(&usernames.counts, usernames.total).to_owned(),
    };

    let timestamp_map = expect_get(&timestamps, &username)?;
    let timestamp = weighted_random(&timestamp_map.counts, timestamp_map.total);

    let first_word_map = expect_get(&first_words, &username)?;
    let mut word_norm = weighted_random(&first_word_map.counts, first_word_map.total);

    let mut words = Vec::<Word>::new();
    loop {
        if word_norm.is_empty() {
            break;
        }
        let variants = expect_get(&alternatives, &word_norm)?;
        words.push(get_word(&weighted_random(&variants.counts, variants.total)));
        let next_word_map = expect_get(&word_map, &word_norm)?;
        word_norm = weighted_random(&next_word_map.counts, next_word_map.total);
    }

    json_response(json!({
        "message": words,
        "timestamp": timestamp,
        "username": username,
    }))
}

#[handler]
async fn sources() -> poem::Result<Response> {
    let data = METADATA.lock().map_err(InternalError::new)?;
    json_response(data.deref())
}

fn json_response<T: Serialize>(body: T) -> poem::Result<Response> {
    Ok(Response::builder()
        .content_type("application/json")
        .body(Body::from_json(body).map_err(InternalError::new)?))
}

fn expect_get<'a, T>(map: &'a HashMap<String, T>, word: &'a str) -> Result<&'a T, InternalError> {
    map.get(word).ok_or_else(|| {
        InternalError::new(format!(
            "could not find word `{}` supposed to be in map",
            word
        ))
    })
}

macro_rules! get {
    ($endpoint:ident) => {
        poem::get($endpoint).head($endpoint)
    };
}

fn get_word(text: &str) -> Word {
    if let Some(&id) = BTTV_EMOTES.get(text) {
        return Word::Emote(Emote {
            id: id.to_owned(),
            name: text.to_owned(),
            source: "bttv".to_owned(),
        });
    }
    if let Some(&id) = TWITCH_EMOTES.get(text) {
        return Word::Emote(Emote {
            id: id.to_owned(),
            name: text.to_owned(),
            source: "twitch".to_owned(),
        });
    }
    Word::Text(text.to_owned())
}

fn normalize_word(word: &str) -> String {
    if BTTV_EMOTES.contains_key(word) || TWITCH_EMOTES.contains_key(word) {
        return word.to_owned();
    }

    let word = word.to_lowercase();
    let normalized = NORMALIZE_RE.replace_all(&word, "");
    if normalized.is_empty() {
        word
    } else {
        normalized.to_string()
    }
}

fn weighted_random<T: std::fmt::Display>(counts: &HashMap<T, usize>, total: usize) -> &T {
    let random = thread_rng().gen_range(0..total);
    let mut sum = 0;
    for (item, count) in counts {
        sum += count;
        if random < sum {
            return item;
        }
    }
    panic!("weighted_random did not find anything");
}

pub fn create_app(chatlog_directory: &PathBuf) -> impl Endpoint<Output = Response> {
    let mut alternatives = ALTERNATIVES.lock().unwrap();
    let mut first_words = FIRST_WORDS.lock().unwrap();
    let mut metadata = METADATA.lock().unwrap();
    let mut timestamps = TIMESTAMPS.lock().unwrap();
    let mut usernames = USERNAMES.lock().unwrap();
    let mut word_map = WORD_MAP.lock().unwrap();

    struct LogFile {
        path: PathBuf,
        channel_name: String,
        date: NaiveDate,
    }

    let chatlog_re = Regex::new(r"^(.+)-(\d{4}-\d{2}-\d{2})\.log$").unwrap();
    let message_re = Regex::new(r"^\[(\d{2}:\d{2}:\d{2})\]  (.+)$").unwrap();
    let whitespace_re = Regex::new(r"\s+").unwrap();

    let mut warnings = HashSet::<String>::new();

    let files: Vec<_> = chatlog_directory
        .read_dir()
        .expect("could not open directory")
        .filter_map(|entry| {
            let entry = match entry {
                Ok(entry) => entry,
                Err(err) => {
                    warnings.insert(format!("{}", err));
                    return None;
                }
            };
            let path = entry.path();
            let (channel_name, date) = {
                let file_name = entry.file_name();
                let file_name = match file_name.to_str() {
                    Some(file_name) => file_name,
                    None => {
                        warnings.insert(format!(
                            "invalid file name: {}",
                            file_name.to_string_lossy()
                        ));
                        return None;
                    }
                };
                let captures = match chatlog_re.captures(file_name) {
                    Some(captures) => captures,
                    None => {
                        warnings.insert(format!("invalid file name format: {}", file_name));
                        return None;
                    }
                };
                let channel_name = captures.get(1).unwrap().as_str().to_owned();
                let date = captures.get(2).unwrap().as_str();
                let date = match NaiveDate::parse_from_str(date, "%Y-%m-%d") {
                    Ok(date) => date,
                    Err(_) => {
                        warnings.insert(format!("invalid date in file name: {}", date));
                        return None;
                    }
                };
                (channel_name, date)
            };
            Some(LogFile {
                path,
                channel_name,
                date,
            })
        })
        .collect();

    for log_file in files {
        let file = match File::open(&log_file.path) {
            Ok(file) => file,
            Err(err) => {
                warnings.insert(format!(
                    "could not open {}: {}",
                    log_file.path.to_string_lossy(),
                    err
                ));
                continue;
            }
        };

        let mut lines = 0;

        for (index, line) in BufReader::new(file).lines().enumerate() {
            let line = match line {
                Ok(line) => line,
                Err(err) => {
                    warnings.insert(format!(
                        "could not read line {} in {}: {}",
                        index,
                        log_file.path.to_string_lossy(),
                        err
                    ));
                    continue;
                }
            };
            let captures = match message_re.captures(&line) {
                Some(captures) => captures,
                None => {
                    warnings.insert(format!("invalid format for line: {}", line));
                    continue;
                }
            };

            let timestamp = match captures.get(1) {
                Some(timestamp) => timestamp.as_str(),
                None => {
                    warnings.insert(format!("invalid timestamp format: {}", line));
                    continue;
                }
            };

            if let Some(message) = captures.get(2) {
                let mut words = vec![""];
                let mut split_message = whitespace_re.split(message.as_str());

                let username = match split_message.next() {
                    Some(username) => username,
                    None => {
                        warnings.insert(format!("empty message: {}", line));
                        continue;
                    }
                };

                words.extend(split_message);
                if words.len() < MIN_MESSAGE_WORDS + 1 {
                    continue;
                }

                let username = match username.strip_suffix(':') {
                    Some(username) => username,
                    None => {
                        warnings.insert(format!("invalid username: {}", line));
                        continue;
                    }
                };

                if let Some(count) = usernames.counts.get_mut(username) {
                    *count += 1;
                } else {
                    usernames.counts.insert(username.to_owned(), 1);
                }
                usernames.total += 1;

                if let Some(timestamps_map) = timestamps.get_mut(username) {
                    if let Some(count) = timestamps_map.counts.get_mut(timestamp) {
                        *count += 1;
                    } else {
                        timestamps_map.counts.insert(timestamp.to_owned(), 1);
                    }
                    timestamps_map.total += 1;
                } else {
                    timestamps.insert(
                        username.to_owned(),
                        CountMap::new_with_item(timestamp.to_owned()),
                    );
                }

                let first_word = normalize_word(words[1]);
                if let Some(first_words_map) = first_words.get_mut(username) {
                    if let Some(count) = first_words_map.counts.get_mut(&first_word) {
                        *count += 1;
                    } else {
                        first_words_map.counts.insert(first_word, 1);
                    }
                    first_words_map.total += 1;
                } else {
                    first_words.insert(username.to_owned(), CountMap::new_with_item(first_word));
                }

                words.push("");
                for (&current, &next) in words.iter().zip(&words[1..]) {
                    let current_norm = normalize_word(&current);
                    if let Some(alts) = alternatives.get_mut(&current_norm) {
                        if let Some(count) = alts.counts.get_mut(current) {
                            *count += 1;
                        } else {
                            alts.counts.insert(current.to_owned(), 1);
                        }
                        alts.total += 1;
                    } else {
                        alternatives.insert(
                            current_norm.clone(),
                            CountMap::new_with_item(current.to_owned()),
                        );
                    }

                    let next_norm = normalize_word(next);
                    if let Some(word_map_inner) = word_map.get_mut(&current_norm) {
                        if let Some(count) = word_map_inner.counts.get_mut(&next_norm) {
                            *count += 1;
                        } else {
                            word_map_inner.counts.insert(next_norm, 1);
                        }
                        word_map_inner.total += 1;
                    } else {
                        word_map.insert(current_norm, CountMap::new_with_item(next_norm));
                    }
                }
                lines += 1;
            } else {
                warnings.insert(format!("invalid message format: {}", line));
                continue;
            }
        }

        if let Some(channel_meta) = metadata.get_mut(&log_file.channel_name) {
            channel_meta.lines += lines;
            channel_meta.log_files += 1;
            if log_file.date < channel_meta.first {
                channel_meta.first = log_file.date;
            }
            if log_file.date > channel_meta.last {
                channel_meta.last = log_file.date;
            }
        } else {
            metadata.insert(
                log_file.channel_name,
                Metadata {
                    lines,
                    log_files: 1,
                    first: log_file.date,
                    last: log_file.date,
                },
            );
        }
    }

    for warning in warnings {
        warn!("{}", warning);
    }

    Route::new()
        .at("/api/v1/generate", get!(generate_quote))
        .at("/api/v1/sources", get!(sources))
        .catch_all_error(error_handler)
}
