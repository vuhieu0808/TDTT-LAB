"""
Module để matching job dựa trên skills và knowledge của user
"""
from typing import List, Dict, Set
from .data_loader import DataLoader
from .data_type import *


class JobMatcher:
    """Class để match jobs với user skills và knowledge"""

    def __init__(self, data_loader: DataLoader):
        """
        Khởi tạo JobMatcher
        
        Args:
            data_loader: Instance của DataLoader
        """
        self.data_loader: DataLoader = data_loader
    
    def calculate_match_score(self, job: Job, user_skills: List[str], 
                            user_knowledge: List[str]) -> Dict:
        """
        Tính điểm phù hợp giữa job và user
        
        Args:
            job: object Job
            user_skills: Danh sách skills của user
            user_knowledge: Danh sách knowledge của user
            
        Returns:
            Dictionary chứa điểm số và thông tin chi tiết
        """
        
        # Tính matched và missing
        matched_required_skills = set(user_skills) & set(job.essential_skill)
        matched_optional_skills = set(user_skills) & set(job.optional_skill)
        matched_required_knowledge = set(user_knowledge) & set(job.essential_knowledge)
        matched_optional_knowledge = set(user_knowledge) & set(job.optional_knowledge)

        missing_required_skills = set(job.essential_skill) - set(user_skills)
        missing_optional_skills = set(job.optional_skill) - set(user_skills)
        missing_required_knowledge = set(job.essential_knowledge) - set(user_knowledge)
        missing_optional_knowledge = set(job.optional_knowledge) - set(user_knowledge)

        # Tính điểm
        # Required: 70% trọng số, Optional: 30% trọng số
        total_required = len(job.essential_skill) + len(job.essential_knowledge)
        total_optional = len(job.optional_skill) + len(job.optional_knowledge)

        matched_required = len(matched_required_skills) + len(matched_required_knowledge)
        matched_optional = len(matched_optional_skills) + len(matched_optional_knowledge)
        
        # Cải thiện: Nếu không có required items, tính điểm dựa trên optional
        if total_required > 0:
            required_score = (matched_required / total_required * 100)
        else:
            required_score = 100  # Nếu job không có required items
        
        if total_optional > 0:
            optional_score = (matched_optional / total_optional * 100)
        else:
            optional_score = 100  # Nếu job không có optional items
        
        # Tổng điểm: Nếu có ít nhất 1 match, cho điểm tối thiểu
        total_match = matched_required + matched_optional
        if total_match > 0:
            # Có match: tính điểm bình thường + bonus
            total_score = required_score * 0.7 + optional_score * 0.3
            # Bonus cho mỗi item matched (tối đa 20 điểm)
            bonus = min(total_match * 5, 20)
            total_score = min(total_score + bonus, 100)
        else:
            # Không có match nào
            total_score = 0
        
        return {
            "job_name": job.name,
            "total_score": round(total_score, 2),
            "required_score": round(required_score, 2),
            "optional_score": round(optional_score, 2),
            "matched": {
                "required_skills": list(matched_required_skills),
                "optional_skills": list(matched_optional_skills),
                "required_knowledge": list(matched_required_knowledge),
                "optional_knowledge": list(matched_optional_knowledge)
            },
            "missing": {
                "required_skills": list(missing_required_skills),
                "optional_skills": list(missing_optional_skills),
                "required_knowledge": list(missing_required_knowledge),
                "optional_knowledge": list(missing_optional_knowledge)
            },
            "total_required": total_required,
            "total_optional": total_optional,
            "matched_required": matched_required,
            "matched_optional": matched_optional
        }
    
    def find_suitable_jobs(self, user_skills: List[str], 
                          user_knowledge: List[str],
                          min_score: float = 5.0,  # Giảm threshold xuống rất thấp
                          top_n: int = 15) -> List[Dict]:  # Tăng số lượng kết quả
        """
        Tìm các công việc phù hợp với user
        
        Args:
            user_skills: Danh sách skills của user
            user_knowledge: Danh sách knowledge của user
            min_score: Điểm tối thiểu để được xem là phù hợp (mặc định 5.0)
            top_n: Số lượng jobs tối đa trả về (mặc định 15)
            
        Returns:
            Danh sách các jobs phù hợp, sắp xếp theo điểm giảm dần
        """
        results = []
        
        for _, job in self.data_loader.jobs_data.items():
            match_info = self.calculate_match_score(job, user_skills, user_knowledge)
            # Chỉ lấy jobs có ít nhất 1 match (score > 0)
            if match_info["total_score"] >= min_score:
                results.append(match_info)
        
        # Sắp xếp theo điểm giảm dần
        results.sort(key=lambda x: x["total_score"], reverse=True)
        
        return results[:top_n]
    
    def get_missing_requirements(self, job_name: str, 
                                user_skills: List[str],
                                user_knowledge: List[str]) -> Dict:
        """
        Lấy danh sách các requirements còn thiếu cho một job cụ thể
        
        Args:
            job_name: Tên công việc
            user_skills: Danh sách skills của user
            user_knowledge: Danh sách knowledge của user
            
        Returns:
            Dictionary chứa thông tin về requirements còn thiếu
        """
        job = self.data_loader.get_job_by_name(job_name)
        
        if not job:
            return {
                "error": f"Job not found: {job_name}",
                "found": False
            }
        
        match_info = self.calculate_match_score(job, user_skills, user_knowledge)
        
        # Thêm thông tin job
        match_info["job_description"] = job.description
        match_info["job_url"] = job.url
        match_info["found"] = True
        
        return match_info
    
    def get_skill_gap_summary(self, match_info: Dict) -> str:
        """
        Tạo summary về skill gap
        
        Args:
            match_info: Kết quả từ calculate_match_score hoặc get_missing_requirements
            
        Returns:
            String mô tả skill gap
        """
        missing = match_info["missing"]
        
        total_missing = (len(missing["required_skills"]) + 
                        len(missing["required_knowledge"]) +
                        len(missing["optional_skills"]) + 
                        len(missing["optional_knowledge"]))
        
        if total_missing == 0:
            return "Bạn đã đáp ứng đầy đủ yêu cầu cho công việc này! 🎉"
        
        summary = []
        
        if missing["required_skills"]:
            summary.append(f"Thiếu {len(missing['required_skills'])} kỹ năng bắt buộc")
        
        if missing["required_knowledge"]:
            summary.append(f"Thiếu {len(missing['required_knowledge'])} kiến thức bắt buộc")
        
        if missing["optional_skills"]:
            summary.append(f"Thiếu {len(missing['optional_skills'])} kỹ năng tùy chọn")
        
        if missing["optional_knowledge"]:
            summary.append(f"Thiếu {len(missing['optional_knowledge'])} kiến thức tùy chọn")
        
        return "Cần bổ sung: " + ", ".join(summary)
    
    def prioritize_missing_items(self, missing: Dict) -> List[str]:
        """
        Sắp xếp độ ưu tiên các items cần học (required trước, optional sau)
        
        Args:
            missing: Dictionary chứa missing items
            
        Returns:
            Danh sách items cần học theo thứ tự ưu tiên
        """
        prioritized = []
        
        # Required items đầu tiên
        prioritized.extend(missing["required_skills"])
        prioritized.extend(missing["required_knowledge"])
        
        # Optional items sau
        prioritized.extend(missing["optional_skills"])
        prioritized.extend(missing["optional_knowledge"])
        
        return prioritized
