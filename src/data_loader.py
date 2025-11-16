"""
Module để load và quản lý dữ liệu từ các file JSON
"""
import json
from typing import Dict, List, Any


class DataLoader:
    """Class để load và quản lý dữ liệu từ các file JSON"""
    
    def __init__(self, data_dir: str = "."):
        """
        Khởi tạo DataLoader
        
        Args:
            data_dir: Thư mục chứa các file dữ liệu
        """
        self.data_dir = data_dir
        self.jobs_data = []
        self.skills_data = []
        self.knowledge_data = []
        self.skill_details = {}  # Dictionary để lưu thông tin chi tiết về skills
        
    def load_all_data(self):
        """Load tất cả dữ liệu từ các file JSON"""
        self.jobs_data = self.load_json("assets/data.json")
        self.skills_data = self.load_json("assets/skill.json")
        self.knowledge_data = self.load_json("assets/knowledge.json")
        self.skill_details = self._parse_skill_details("assets/knowledge.txt")
        
    def load_json(self, filename: str) -> Any:
        """
        Load dữ liệu từ file JSON
        
        Args:
            filename: Tên file cần load
            
        Returns:
            Dữ liệu từ file JSON
        """
        try:
            with open(f"{self.data_dir}/{filename}", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {filename}")
            return []
        except json.JSONDecodeError:
            print(f"Error reading file: {filename}")
            return []
            
    def _parse_skill_details(self, filename: str) -> Dict[str, Dict]:
        """
        Parse file knowledge.txt để lấy thông tin chi tiết về skills
        
        Args:
            filename: Tên file chứa thông tin skills
            
        Returns:
            Dictionary với key là tên skill và value là thông tin chi tiết
        """
        try:
            with open(f"{self.data_dir}/{filename}", "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    item["skill"].lower(): {
                        "level": item["level"],
                        "detailed": item["detailed"],
                        "prerequisites": item["prerequisites"]
                    }
                    for item in data
                }
        except Exception as e:
            print(f"Error parsing skill details: {e}")
            return {}
    
    def get_job_by_name(self, job_name: str) -> Dict:
        """
        Lấy thông tin job theo tên
        
        Args:
            job_name: Tên công việc
            
        Returns:
            Thông tin công việc hoặc None
        """
        job_name_lower = job_name.lower()
        for job in self.jobs_data:
            if job["name"].lower() == job_name_lower:
                return job
            # Kiểm tra cả các tên khác
            if "other_name" in job:
                for other in job["other_name"]:
                    if other.lower() == job_name_lower:
                        return job
        return None
    
    def get_skill_info(self, skill_name: str) -> Dict:
        """
        Lấy thông tin chi tiết về skill
        
        Args:
            skill_name: Tên kỹ năng
            
        Returns:
            Thông tin chi tiết về skill
        """
        return self.skill_details.get(skill_name.lower(), {
            "level": 5,  # Default level 5 if not found
            "detailed": [],
            "prerequisites": []
        })
    
    def get_knowledge_info(self, knowledge_name: str) -> Dict:
        """
        Lấy thông tin chi tiết về knowledge (cũng từ knowledge.txt)
        
        Args:
            knowledge_name: Tên kiến thức
            
        Returns:
            Thông tin chi tiết về knowledge
        """
        return self.skill_details.get(knowledge_name.lower(), {
            "level": 5,
            "detailed": [],
            "prerequisites": []
        })
    
    def search_jobs(self, query: str) -> List[Dict]:
        """
        Tìm kiếm jobs theo tên
        
        Args:
            query: Từ khóa tìm kiếm
            
        Returns:
            Danh sách các jobs phù hợp
        """
        query_lower = query.lower()
        results = []
        for job in self.jobs_data:
            if query_lower in job["name"].lower():
                results.append(job)
            elif "other_name" in job:
                for other in job["other_name"]:
                    if query_lower in other.lower():
                        results.append(job)
                        break
        return results
    
    def get_all_jobs(self) -> List[str]:
        """Lấy danh sách tất cả các job names"""
        return [job["name"] for job in self.jobs_data]
    
    def get_all_skills(self) -> List[str]:
        """Lấy danh sách tất cả các skills"""
        return self.skills_data
    
    def get_all_knowledge(self) -> List[str]:
        """Lấy danh sách tất cả các knowledge"""
        return self.knowledge_data
