import 'dart:convert';

import 'package:fetch_esco/impl.dart';
import 'dart:io';

Future<void> setupDirectory(String path) async {
  final newDir = Directory(path);
  stdout.write("Creating directory for data...");
  if(newDir.existsSync()) {
    stdout.writeln('already exists');
    return;
  }
  try {
    newDir.createSync(recursive: true);
    stdout.writeln('success');
  } catch (e) {
    stdout.writeln('failed: $e');
    rethrow;
  }
}

void writeJson(String jsonFile) {
  final file = File(jsonFile);
  List<dynamic> jsonArray = [];
  for(var ele in globalDataList) {
    jsonArray.add(ele.toJson());
  }

  String jsonString = jsonEncode(jsonArray);
  
  try {
    file.writeAsStringSync(
      jsonString,
      mode: FileMode.write,
    );
    print('Written ${jsonFile}');
  } catch (e) {
    print('Error writing json file: $e');
  }
}

Set<String> tmpset = {};

void main(List<String> arguments) async {
  await setupDirectory("data");
  await dfs(initialRequestUrl);
  print("Total ${globalDataList.length} occupations");
  writeJson("data/data.json");

  for(var ele in globalDataList) {
    tmpset.addAll(ele.essentialKnowledge.map((e) => e.toString()));
    tmpset.addAll(ele.optionalKnowledge.map((e) => e.toString()));
  }
  try {
    File("data/knowledge.json").writeAsStringSync(
      json.encode(tmpset.toList()),
      mode: FileMode.write,
    );
    print('Written knowledge.json');
  } catch (e) {
    print('Error writing knowledge.json: $e');
  }
  
  tmpset.clear();
  for(var ele in globalDataList) {
    tmpset.addAll(ele.essentialSkill.map((e) => e.toString()));
    tmpset.addAll(ele.optionalSkill.map((e) => e.toString()));
  }
  try {
    File("data/skill.json").writeAsStringSync(
      json.encode(tmpset.toList()),
      mode: FileMode.write,
    );
    print('Written skill.json');
  } catch (e) {
    print('Error writing skill.json: $e');
  }
}
