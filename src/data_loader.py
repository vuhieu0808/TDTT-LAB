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
        self.detailed_to_canonical = {}  # Map từ detailed item -> canonical skill/knowledge
        self.canonical_to_detailed = {}  # Map từ canonical -> list of detailed items
        self.job_other_name_to_canonical = {}  # Map từ other_name -> canonical job name
        
        # Cache expanded skills/knowledge để tránh tính toán lại
        self.expanded_skills_cache = None
        self.expanded_knowledge_cache = None
        
    def load_all_data(self):
        """Load tất cả dữ liệu từ các file JSON"""
        self.jobs_data = self.load_json("assets/data.json")
        self.skills_data = self.load_json("assets/skill.json")
        self.knowledge_data = self.load_json("assets/knowledge.json")
        self.skill_details = self._parse_skill_details("assets/knowledge.txt")
        self._build_mapping_tables()  # Build mapping tables sau khi load data
        self._build_expanded_cache()  # Build cache cho expanded skills/knowledge
        
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
    
    def _build_mapping_tables(self):
        """
        Build các bảng mapping:
        - detailed items -> canonical skill/knowledge
        - canonical -> list of detailed items
        - job other_name -> canonical job name
        """
        # Build skill/knowledge mappings từ knowledge.txt
        for canonical_name, info in self.skill_details.items():
            detailed_items = info.get("detailed", [])
            self.canonical_to_detailed[canonical_name] = detailed_items
            
            # Map mỗi detailed item về canonical name
            for detailed_item in detailed_items:
                detailed_lower = detailed_item.lower()
                self.detailed_to_canonical[detailed_lower] = canonical_name
        
        # Build job other_name mappings
        for job in self.jobs_data:
            canonical_job_name = job["name"]
            other_names = job.get("other_name", [])
            
            for other_name in other_names:
                other_name_lower = other_name.lower()
                self.job_other_name_to_canonical[other_name_lower] = canonical_job_name
    
    def get_canonical_skill_or_knowledge(self, item_name: str) -> str:
        """
        Map một skill/knowledge name (có thể là detailed item) về canonical name
        
        Args:
            item_name: Tên skill/knowledge (có thể là detailed item như "React.js")
            
        Returns:
            Canonical name (ví dụ: "javascript framework")
        """
        item_lower = item_name.lower()
        
        # Kiểm tra xem đây có phải là detailed item không
        if item_lower in self.detailed_to_canonical:
            return self.detailed_to_canonical[item_lower]
        
        # Nếu không, trả về chính nó (có thể đã là canonical)
        return item_lower
    
    def get_canonical_job_name(self, job_name: str) -> str:
        """
        Map một job name (có thể là other_name) về canonical job name
        
        Args:
            job_name: Tên job (có thể là other_name như "devops engineer")
            
        Returns:
            Canonical job name (ví dụ: "cloud DevOps engineer")
        """
        job_lower = job_name.lower()
        
        # Kiểm tra xem đây có phải là other_name không
        if job_lower in self.job_other_name_to_canonical:
            return self.job_other_name_to_canonical[job_lower]
        
        # Kiểm tra xem có phải là canonical name không
        for job in self.jobs_data:
            if job["name"].lower() == job_lower:
                return job["name"]
        
        # Nếu không tìm thấy, trả về chính nó
        return job_name
    
    def get_expanded_skills_and_knowledge(self) -> tuple:
        """
        Lấy danh sách expanded skills và knowledge bao gồm cả detailed items
        
        Returns:
            Tuple (expanded_skills, expanded_knowledge) với format:
            [(display_name, canonical_name), ...]
            Ví dụ: [("React.js → JavaScript Framework", "javascript framework"), ...]
        """
        # Trả về cache nếu đã có
        if self.expanded_skills_cache is not None and self.expanded_knowledge_cache is not None:
            return self.expanded_skills_cache, self.expanded_knowledge_cache
        
        # Nếu chưa có cache và data chưa load xong, trả về empty lists
        if not self.skills_data or not self.knowledge_data:
            return [], []
        
        # Nếu chưa có cache nhưng data đã load, build cache
        self._build_expanded_cache()
        return self.expanded_skills_cache, self.expanded_knowledge_cache
    
    def _build_expanded_cache(self):
        """Build cache cho expanded skills và knowledge"""
        expanded_skills = []
        expanded_knowledge = []
        
        # Thêm tất cả skills từ skill.json (không có detailed items)
        for skill in self.skills_data:
            expanded_skills.append((skill, skill.lower()))
        
        # Thêm tất cả knowledge từ knowledge.json cùng với detailed items
        for knowledge in self.knowledge_data:
            knowledge_lower = knowledge.lower()
            
            # Thêm canonical knowledge
            expanded_knowledge.append((knowledge, knowledge_lower))
            
            # Thêm detailed items nếu có
            info = self.get_knowledge_info(knowledge)
            detailed_items = info.get("detailed", [])
            
            for detailed in detailed_items:
                # Format: "React.js → JavaScript Framework"
                display_name = f"{detailed} → {knowledge}"
                canonical = self.get_canonical_skill_or_knowledge(detailed)
                expanded_knowledge.append((display_name, canonical))
            
            if len(expanded_knowledge) > 400: 
                break


        # Lưu vào cache
        self.expanded_skills_cache = expanded_skills
        self.expanded_knowledge_cache = expanded_knowledge
    
    def get_expanded_job_names(self) -> List[tuple]:
        """
        Lấy danh sách expanded job names bao gồm cả other_names
        
        Returns:
            List of tuples: [(display_name, canonical_name), ...]
            Ví dụ: [("cloud DevOps engineer", "cloud DevOps engineer"), 
                    ("devops engineer → cloud DevOps engineer", "cloud DevOps engineer"), ...]
        """
        expanded_jobs = []
        
        for job in self.jobs_data:
            canonical_name = job["name"]
            
            # Thêm canonical name
            expanded_jobs.append((canonical_name, canonical_name))
            
            # Thêm other_names
            other_names = job.get("other_name", [])
            for other_name in other_names:
                display_name = f"{other_name} → {canonical_name}"
                expanded_jobs.append((display_name, canonical_name))
        
        return expanded_jobs
