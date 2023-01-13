use std::{
    fs::{self, Permissions},
    os::unix::{fs::PermissionsExt, net::UnixListener},
    path::PathBuf,
};

use clap::Parser;
use poem::{listener::UnixAcceptor, Server};

#[derive(Parser)]
struct Args {
    #[arg(short = 'd', long)]
    chatlog_directory: PathBuf,

    #[arg(short, long)]
    socket: PathBuf,
}

#[tokio::main]
async fn main() -> std::io::Result<()> {
    tracing_subscriber::fmt::init();

    let args = Args::parse();

    let socket = UnixListener::bind(&args.socket)?;
    fs::set_permissions(&args.socket, Permissions::from_mode(0o660))?;
    let acceptor = UnixAcceptor::from_std(socket)?;
    Server::new_with_acceptor(acceptor)
        .run(server::create_app(&args.chatlog_directory))
        .await
}
