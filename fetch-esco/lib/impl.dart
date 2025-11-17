import 'dart:io';
import 'dart:async';
import 'dart:convert';
import 'package:fetch_esco/datatypes.dart';
import 'package:http/http.dart' as http;
import 'package:fetch_esco/expected.dart';

const initialRequestUrl = "http://data.europa.eu/esco/isco/C25";

const apiUrl = "ec.europa.eu";
const endpointOccupation = "/esco/api/resource/occupation";
const endpointSkill = "/esco/api/resource/skill";

const txtFile = "data/data.txt";

Future<Expected<Map<String, dynamic>>> makeRequest(String endpoint, List<String> requestUrlList) async {
  final Map<String, dynamic> queryParams = {
    'language': 'en-us',
    'selectedVersion': 'v1.2.0',
    'uris': requestUrlList
  };
  final uri = Uri.https(apiUrl, endpointOccupation, queryParams);
  try {
    final response = await http.get(uri);
    if(response.statusCode != 200) {
      return Expected.failure("HTTP ${response.statusCode}: ${response.body}");
    }

    final jsonData = jsonDecode(response.body) as Map<String, dynamic>;
    return Expected.success(jsonData);
  } catch(e) {
    return Expected.failure(e.toString());
  }
}

List<Occupation> globalDataList = [];

Future<void> writeFile(String filename, String tstr) async {
  final file = File(filename);
  try {
    file.writeAsStringSync(
      "\n$tstr",
      mode: FileMode.append,
    );
  } catch (e) {
    print('Error writing data file: $e');
  }
}

Future<void> dfs(String url) async {
  List<Future<void>> futureList = [];
  stdout.writeln("Fetching $url ....");
  var expectedData = await makeRequest(endpointSkill, [url]);
  if(expectedData.isFailure) {
    stdout.writeln("Failed to fetch: ${expectedData.errorString}");
  } else {
    var jsonData = expectedData.data!["_embedded"] as Map<String, dynamic>;
    for(var ele in jsonData.keys) {
      if(ele.contains("occupation")) {
        var oo = Occupation(jsonData: jsonData[ele]);
        globalDataList.add(oo);
        stdout.writeln("Occupation added: ${oo.name} = $ele");
        // await writeFile(txtFile, oo.toString());
      } else {
        var root = jsonData[ele]["_links"] as Map<String, dynamic>;
        if(root.containsKey("narrowerConcept")) {
          var tmp = root["narrowerConcept"] as List<dynamic>;
          for(var _ele2 in tmp) {
            var ele2 = _ele2 as Map<String, dynamic>;
            var tmp2 = ele2["uri"] as String;
            var promise = dfs(tmp2);
            futureList.add(promise);
          }
        }
        if(root.containsKey("narrowerOccupation")) {
          var tmp = root["narrowerOccupation"] as List<dynamic>;
          for(var _ele2 in tmp) {
            var ele2 = _ele2 as Map<String, dynamic>;
            var tmp2 = ele2["uri"] as String;
            var promise = dfs(tmp2);
            futureList.add(promise);
          }
        }
      }
    }
    await Future.wait(futureList);
  }
}
