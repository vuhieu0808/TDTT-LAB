"""
Module để load và quản lý dữ liệu từ các file JSON
"""
import json
from typing import Dict, List, Any, TypeVar, Callable
from thefuzz import fuzz
from .data_type import *

T = TypeVar("T")

class DataLoader:
    """Class để load và quản lý dữ liệu từ các file JSON"""
    
    def __init__(self, data_dir: str = "."):
        """
        Khởi tạo DataLoader
        
        Args:
            data_dir: Thư mục chứa các file dữ liệu
        """
        self.data_dir = data_dir
        self.jobs_data: Dict[str, Job] = {}
        self.jobs_other_name_map = {}  # Map từ other_name -> job name
        self.skills_data: List[str] = self.load_json("assets/skill.json")
        self.knowledge_data: Dict[str, Knowledge] = {}
        self.knowledge_detail_map: Dict[str, str] = {}    # map từ knowledge detailed item -> knowledge name

        self.load_jobs_json("assets/job.json")
        self.load_knowledges_json("assets/knowledge2.json")

        # Cache expanded skills/knowledge để tránh tính toán lại
        self.expanded_skills_cache = None
        self.expanded_knowledge_cache = None
        
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
            
    def load_jobs_json(self, filename: str) -> None:
        try:
            with open(f"{self.data_dir}/{filename}", "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    job = Job(item)
                    job_name_normalized = job.name.lower()
                    self.jobs_data[job_name_normalized] = job
                    for other_name in job.other_name:
                        self.jobs_other_name_map[other_name.lower()] = job_name_normalized
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except json.JSONDecodeError:
            print(f"Error reading file: {filename}")

    def load_knowledges_json(self, filename: str) -> None:
        try:
            with open(f"{self.data_dir}/{filename}", "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    knowledge = Knowledge(item)
                    knowledge_name_normalized = knowledge.name.lower()
                    self.knowledge_data[knowledge_name_normalized] = knowledge

                    for detailed_item in knowledge.detailed:
                        self.knowledge_detail_map[detailed_item.lower()] = knowledge_name_normalized
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except json.JSONDecodeError:
            print(f"Error reading file: {filename}")
    
    def get_job_by_name(self, job_name: str) -> Job | None:
        """
        Lấy thông tin job theo tên. Tự động map các tên khác (other_name) về tên chính
        
        Args:
            job_name: Tên công việc
            
        Returns:
            Job object hoặc None nếu không tìm thấy
        """
        return self.jobs_data.get(job_name.lower())
    
    def get_knowledge_info(self, knowledge_name: str) -> Knowledge | None:
        """
        Lấy thông tin chi tiết về knowledge (cũng từ knowledge.txt)
        
        Args:
            knowledge_name: Tên kiến thức
            
        Returns:
            Thông tin chi tiết về knowledge
        """
        return self.knowledge_data.get(knowledge_name.lower())

    def _impl_search_dict_keys(self, query: str, dict: Dict[str, T], compare_func: Callable[[str, str], int], threshold: int) -> List[tuple[int, str]]:
        query = query.lower()
        vec: List[tuple[int, str]] = []
        for key, _ in dict.items():
            score = compare_func(key, query)
            if score >= threshold:
                vec.append((score, key))
        return vec
    
    def _impl_search_list(self, query: str, list: List[str], compare_func: Callable[[str, str], int], threshold: int) -> List[tuple[int, str]]:
        query = query.lower()
        vec: List[tuple[int, str]] = []
        for key in list:
            score = compare_func(key, query)
            if score >= threshold:
                vec.append((score, key))
        return vec
    
    def search_jobs(self, query: str, limit: int) -> List[str]:
        """
        Tìm kiếm jobs theo tên (bao gồm other_name), sử dụng fuzzy sort 
        
        Args:
            query: Từ khóa tìm kiếm
            
        Returns:
            Danh sách các jobs phù hợp, theo string
        """
        score_threshold = 65
        query = query.lower()
        vec : List[tuple[int, str]] = []
        for key, _ in self.jobs_data.items():
            score = fuzz.token_set_ratio(key, query)
            if score >= score_threshold:
                vec.append((score, key))

        for key, _ in self.jobs_other_name_map.items():
            score = fuzz.token_set_ratio(key, query)
            if score >= score_threshold:
                vec.append((score, key))

        vec.sort(reverse=True, key=lambda x: x[0])
        result: List[str] = [item[1] for item in vec]

        return result[:limit]

    def search_skill(self, query: str, limit: int) -> List[str]:
        """
        Tìm kiếm skill theo tên (bao gồm other_name), sử dụng fuzzy sort

        Args:
            query: Từ khóa tìm kiếm

        Returns:
            Danh sách các skill phù hợp, theo string
        """
        vec : List[tuple[int, str]] = []
        vec += self._impl_search_list(query, self.skills_data, fuzz.token_sort_ratio, 70)

        vec.sort(reverse=True, key=lambda x: x[0])
        result: List[str] = [item[1] for item in vec]

        return result[:limit]

    def search_knowledges(self, query: str, limit: int) -> List[str]:
        """
        Tìm kiếm knowledge theo tên (bao gồm detailed), sử dụng fuzzy sort 

        Args:
            query: Từ khóa tìm kiếm
            
        Returns:
            Danh sách các knowledge phù hợp, theo string
        """
        vec : List[tuple[int, str]] = []
        vec += self._impl_search_dict_keys(query, self.knowledge_data, fuzz.token_set_ratio, 65)
        vec += self._impl_search_dict_keys(query, self.knowledge_detail_map, fuzz.token_set_ratio, 65)

        vec.sort(reverse=True, key=lambda x: x[0])
        result: List[str] = [item[1] for item in vec]

        return result[:limit]
    
    def search_knowledges2(self, query: str, limit: int) -> List[str]:
        """
        Alternative parameter for fuzzysearch
        """
        vec : List[tuple[int, str]] = []
        vec += self._impl_search_dict_keys(query, self.knowledge_data, fuzz.token_sort_ratio, 70)
        vec += self._impl_search_dict_keys(query, self.knowledge_detail_map, fuzz.token_sort_ratio, 70)

        vec.sort(reverse=True, key=lambda x: x[0])
        result: List[str] = [item[1] for item in vec]

        return result[:limit]