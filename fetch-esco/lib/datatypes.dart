abstract class SkillBase {
  final String name; 
  final String url;

  SkillBase({required Map<String, dynamic> jsonData})
      : name = jsonData["title"] as String,
        url = jsonData["uri"] as String;

  String type();
  
  @override
  String toString() => name;
}

class SkillData extends SkillBase {
  @override String type() => "skill";

  SkillData._internal({required super.jsonData});

  factory SkillData({required Map<String, dynamic> jsonData}) {
    // String givenType = jsonData["skillType"];
    // if(givenType != "http://data.europa.eu/esco/skill-type/skill") {
    //   throw Exception("Invalid skill type given");
    // }
    return SkillData._internal(jsonData: jsonData);
  }
}

class KnowledgeData extends SkillBase {
  @override String type() => "knowledge";

  KnowledgeData._internal({required super.jsonData});

  factory KnowledgeData({required Map<String, dynamic> jsonData}) {
    String givenType = jsonData["skillType"];
    if(givenType != "http://data.europa.eu/esco/skill-type/knowledge") {
      throw Exception("Invalid skill type given");
    }
    return KnowledgeData._internal(jsonData: jsonData);
  }
}

class Occupation {
  late String name;
  late String url;
  late String description;
  List<String> alternativeNameList = [];
  List<SkillData> essentialSkill = [];
  List<SkillData> optionalSkill = [];
  List<KnowledgeData> essentialKnowledge = [];
  List<KnowledgeData> optionalKnowledge = [];

  Occupation({required Map<String, dynamic> jsonData}) {
    //parse english only-data
    name = jsonData["title"] as String; 
    url = jsonData["uri"] as String; 
    description = jsonData["description"]["en"]["literal"] as String;
    List<dynamic> tmp = jsonData["alternativeLabel"]["en"];
    alternativeNameList = tmp.map((e) => e.toString()).toList();

    List<dynamic> tmp2 = jsonData["_links"]["hasEssentialSkill"];
    for(dynamic _d in tmp2) {
      Map<String, dynamic> d = _d as Map<String, dynamic>;
      SkillBase tmp;
      try {
        tmp = KnowledgeData(jsonData: d);
        essentialKnowledge.add(tmp as KnowledgeData);
      } catch(e) {
        //skillType element might not be presented so treating nothing as skill
        tmp = SkillData(jsonData: d);
        essentialSkill.add(tmp as SkillData);
      }
    }

    tmp2 = jsonData["_links"]["hasOptionalSkill"];
    for(dynamic _d in tmp2) {
      Map<String, dynamic> d = _d as Map<String, dynamic>;
      SkillBase tmp;
      try {
        tmp = KnowledgeData(jsonData: d);
        optionalKnowledge.add(tmp as KnowledgeData);
      } catch(e) {
        //skillType element might not be presented so treating nothing as skill
        tmp = SkillData(jsonData: d);
        optionalSkill.add(tmp as SkillData);
      }
    }
  }

  @override
  String toString() {
    List<String> strlist = [];
    strlist.add("Occupation: $name");
    strlist.add(url);
    strlist.add("Description: $description");
    strlist.add("Other names: $alternativeNameList");
    strlist.add("Essential knowledges: $essentialKnowledge");
    strlist.add("Optional knowledges: $optionalKnowledge");
    strlist.add("Essential skills: $essentialSkill");
    strlist.add("Optional skills: $optionalSkill");
    String str = "";
    for(var ele in strlist) {
      str = "$str$ele\n";
    }
    return str;
  }

  Map<String, dynamic> toJson() {
    return {
      "url": url,
      "name": name,
      "description": description,
      "other_name": alternativeNameList,
      "essential_skill": essentialSkill.map((e) => e.toString()).toList(),
      "optional_skill": optionalSkill.map((e) => e.toString()).toList(),
      "essential_knowledge": essentialKnowledge.map((e) => e.toString()).toList(),
      "optional_knowledge": optionalKnowledge.map((e) => e.toString()).toList(),
    };
  }
}

class Concept {

}