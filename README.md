# Nyakov

Generates fake chat from Twitch chatlogs with Markov chains.

## Usage
I have this repository sitting at `/home/nyakov/nyakov/`. By default the server listens on the Unix socket `nyakov.sock` in the runtime directory created by systemd. Tweak `run` and `nyakov.service` to change these.

0. Collect chatlogs from Chatterino to a directory (the `run` script uses `chatlogs/` in the repository root by default); log files are expected to be named like `channelname-yyyy-mm-dd.log`. You may want to use e.g. [process-twitch-log](https://github.com/pettinen/process-twitch-log) to purge stupid shit from logs.

1. To build the server:
```sh
cd server/
cargo build --release
```

2. To build the frontend (I use `pnpm` but `npm` should work too):
```sh
cd client/
pnpm install
pnpm build
```

3. To run as a systemd service:
```sh
sudo cp nyakov.service /usr/local/lib/systemd/system/
sudo systemctl enable --now nyakov
```

4. Configure a web server to serve `client/dist/` and proxy `/api/` to the socket (see `nginx.example.conf`)

5. ???

6. ??????
