import "dart:io";
import "dart:math";

import 'package:path/path.dart';


final rng = Random();


Future<void> main(List<String> args) async {
  if (args.length != 1) {
    print("Usage: nyakov <chatlog directory>");
    exit(1);
  }

  final dir = Directory(args[0]);
  if (!await dir.exists()) {
    print("Chatlog directory not found.");
    exit(1);
  }

  final lines = dir.list()
    .where((entity) => entity is File && extension(entity.path) == ".log")
    .map((entity) => entity as File)
    .expand((file) => file.readAsLinesSync());

  final wordMap = <String, Map<String, int>>{"": {}};
  final alternatives = <String, List<String>>{};
  final timestamps = <String>{};

  final messageRegExp = URegExp(r"^(\[\d\d:\d\d:\d\d\])  (.+)$");
  final outputRegExp = URegExp(r"^\[\d\d:\d\d:\d\d\] \w+:");
  final normalizeRegExp = URegExp(r"[-';!?_@,.]");

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

      final currentNorm = normalizeWord(current, normalizeRegExp);
      final nextNorm = normalizeWord(next, normalizeRegExp);

      if (alternatives[currentNorm] == null)
        alternatives[currentNorm] = [];
      alternatives[currentNorm]?.add(current);

      if (!wordMap.containsKey(currentNorm))
        wordMap[currentNorm] = {};

      int? value = wordMap[currentNorm]![nextNorm];
      if (value == null)
        value = 0;

      value++;
      wordMap[currentNorm]![nextNorm] = value;
    }

    timestamps.add(match[1]!);
  }

  List<String> words;
  String output;
  do {
    words = generateWords(wordMap, alternatives, timestamps);
    output = words.join(" ");
  } while (words.length < 4 || !outputRegExp.hasMatch(output));
  print(output);
}


List<String> generateWords(
  Map<String, Map<String, int>> wordMap,
  Map<String, List<String>> alternatives,
  Set<String> timestamps,
) {
  final normalizedWords = <String>[];
  normalizedWords.add(randomElement(timestamps));

  var word = weightedRandom(wordMap[""]!);
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


String normalizeWord(String word, RegExp pattern) {
  final normalized = word.toLowerCase().replaceAll(pattern, "");
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
