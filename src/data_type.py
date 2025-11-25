from typing import Dict, List, Any

class Job:
    def __init__(self, jsonData: Dict[str, Any]):
        self.name: str = jsonData.get("name", "")
        self.description: str = jsonData.get("description", "")
        self.url: str = jsonData.get("url", "")
        self.other_name: List[str] = jsonData.get("other_name", [])
        self.essential_skill: List[str] = jsonData.get("essential_skill", [])
        self.optional_skill: List[str] = jsonData.get("optional_skill", [])
        self.essential_knowledge: List[str] = jsonData.get("essential_knowledge", [])
        self.optional_knowledge: List[str] = jsonData.get("optional_knowledge", [])
    
    def __repr__(self) -> str:
        return f"Job(name={self.name})"
    
class Knowledge:
    def __init__(self, jsonData: Dict[str, Any]):
        self.name: str = jsonData.get("skill", "")
        self.level: int = jsonData.get("level", 5)
        self.detailed: List[str] = jsonData.get("detailed", [])
        self.prerequisites: List[str] = jsonData.get("prerequisites", [])
    
    def __repr__(self) -> str:
        return f"Knowledge(skill={self.name}, level={self.level})"