import "dart:convert";
import "dart:io";
import "dart:math";

import "package:path/path.dart";


final rng = Random();


Future<void> main(List<String> args) async {
  if (args.length != 1) {
    print("Usage: nyakov <chatlog directory>");
    exit(2);
  }

  final dir = Directory(args[0]);
  if (!await dir.exists()) {
    print("Chatlog directory not found.");
    exit(2);
  }

  final listenPort = int.tryParse(Platform.environment["NYAKOV_PORT"] ?? "", radix: 10);
  if (listenPort == null || listenPort < 49152 || listenPort > 65535) {
    print("NYAKOV_PORT must be an integer between 49152 and 65535.");
    exit(2);
  }

  var wordMap = <String, Map<String, int>>{};
  var alternatives = <String, List<String>>{};
  var timestamps = <String>{};

  var dataFile = File(join(args[0], "nyakov-data.json"));

  if (await dataFile.exists()) {
    var data = jsonDecode(await dataFile.readAsString());

    for (final entry1 in data["wordMap"].entries) {
      wordMap[entry1.key] = {};
      for (final entry2 in entry1.value.entries)
        wordMap[entry1.key]?[entry2.key] = entry2.value;
    }

    for (final entry in data["alternatives"].entries) {
      alternatives[entry.key] = [];
      for (final value in entry.value)
        alternatives[entry.key]?.add(value);
    }

    for (final timestamp in data["timestamps"])
      timestamps.add(timestamp);
  } else {
    final lines = dir.list()
      .where((entity) => entity is File && extension(entity.path) == ".log")
      .map((entity) => entity as File)
      .expand((file) => file.readAsLinesSync());

    wordMap = {"": {}};
    alternatives = {};
    timestamps = {};

    final messageRegExp = URegExp(r"^(\[\d\d:\d\d:\d\d\])  (.+)$");

    await for (var line in lines) {
      final match = messageRegExp.firstMatch(line);
      if (match == null)
        continue;

      final message = match[2];
      if (message == null)
        continue;

      final words = message.split(URegExp(r"\s+"));
      if (words.length < 3)
        continue;

      for (var i = -1; i < words.length; i++) {
        final current = i == -1 ? "" : words[i];
        final next = i == words.length - 1 ? "" : words[i + 1];

        final currentNorm = normalizeWord(current);
        final nextNorm = normalizeWord(next);

        if (alternatives[currentNorm] == null)
          alternatives[currentNorm] = [];
        alternatives[currentNorm]?.add(current);

        if (!wordMap.containsKey(currentNorm))
          wordMap[currentNorm] = {};

        int? value = wordMap[currentNorm]?[nextNorm];
        if (value == null)
          value = 0;

        value++;
        wordMap[currentNorm]?[nextNorm] = value;
      }
      timestamps.add(match[1]!);
    }

    var data = {
      "wordMap": wordMap,
      "alternatives": alternatives,
      "timestamps": timestamps.toList(),
    };
    await dataFile.writeAsString(jsonEncode(data));
  }

  HttpServer.bind(InternetAddress.loopbackIPv4, listenPort).then((server) {
    server.listen((HttpRequest request) {
      List<String> words;
 
      var username = request.uri.queryParameters["user"];
      if (username is String && username.isEmpty)
        username = null;
      if (username != null && !wordMap.containsKey(normalizeWord("$username:"))) {
        request.response.statusCode = HttpStatus.badRequest;
        request.response.write(jsonEncode({"error": "user-not-found"}));
        request.response.close();
        return;
      }

      do {
        words = generateWords(wordMap, alternatives, timestamps, username);
      } while (words.length < 4);

      request.response.write(jsonEncode({
        "timestamp": words[0],
        "username": words[1],
        "words": words.sublist(2),
      }));
      request.response.close();
    });
  });
}


List<String> generateWords(
  Map<String, Map<String, int>> wordMap,
  Map<String, List<String>> alternatives,
  Set<String> timestamps,
  [String? username]
) {
  final normalizedUsername = username != null ? normalizeWord("$username:") : null;

  final normalizedWords = [
    randomElement(timestamps),
    if (normalizedUsername != null) normalizedUsername,
  ];

  var firstWord = username != null ? normalizedUsername : "";
  var word = weightedRandom(wordMap[firstWord]!);
  while (word.isNotEmpty) {
    normalizedWords.add(word);
    word = weightedRandom(wordMap[word]!);
  }

  final words = <String>[];
  for (final word in normalizedWords) {
    if (alternatives[word] == null)
      words.add(word);
    else
      words.add(randomElement(alternatives[word]!));
  }
  return words;
}


String normalizeWord(String word) {
  final normalized = word.toLowerCase().replaceAll(URegExp(r"""[-';!?_@,."']"""), "");
  if (normalized.isEmpty)
    return word.toLowerCase();
  return normalized;
}


String randomElement(Iterable<String> iterable) {
  var list = iterable.toList();
  return list[rng.nextInt(list.length)];
}


RegExp URegExp(String pattern) => RegExp(pattern, unicode: true);


String weightedRandom(Map<String, int> map) {
  final words = <String>[];
  for (final entry in map.entries) {
    for (var i = 0; i < entry.value; i++)
      words.add(entry.key);
  }
  return randomElement(words);
}
