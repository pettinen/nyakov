# Nyakov

Generates fake chat from Twitch chatlogs with Markov chains.

## Usage
I have this repository sitting at `/home/nyakov/nyakov/`. The generator server listens on randomly chosen port 50903, which the Dart and Python servers read from the environment variable `NYAKOV_PORT`. Tweak `run` and `nyakov.service` to change these.

0. Collect chatlogs from Chatterino to a directory (the `run` script uses `chatlogs/` in the repository root by default); only files with the `.log` extension will be read. You may want to use e.g. [process-twitch-log](https://github.com/pettinen/process-twitch-log) to purge stupid shit from logs.

1. To build the generator server:
```sh
cd nyakov/
dart pub get
dart2native -o build/server src/server.dart
```

2. To install Python dependencies:
```sh
cd www-backend/
poetry install
```

3. To build the frontend (I used `pnpm` but `npm` should work too):
```sh
cd www-frontend/
pnpm install
pnpm build
```

4. To run as a systemd service:
```sh
cp nyakov.service /etc/systemd/system/
systemctl enable --now nyakov
```

5. Configure a web server to serve `www-frontend/dist/` and proxy `/api/` to uWSGI (see `nginx.example.conf`)

6. ???

7. ??????
