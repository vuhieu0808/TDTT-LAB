"""
Module tạo roadmap học tập dựa trên topological sort
"""
from typing import List, Dict
from graph_utils import create_roadmap
from data_loader import DataLoader

class RoadmapGenerator:
    """Class để tạo roadmap học tập"""
    
    def __init__(self, data_loader: DataLoader):
        """
        Khởi tạo RoadmapGenerator
        
        Args:
            data_loader: Instance của DataLoader
        """
        self.data_loader = data_loader
    
    def generate_learning_roadmap(self, missing_skills: List[str], 
                                    missing_knowledge: List[str],
                                    learned_knowledge: List[str] | None = None) -> Dict:
        """
        Tạo roadmap học tập chỉ cho knowledge còn thiếu (bỏ skills)
        
        Args:
            missing_skills: Danh sách skills còn thiếu (không sử dụng)
            missing_knowledge: Danh sách knowledge còn thiếu
            learned_knowledge: Danh sách knowledge mà user đã học
            
        Returns:
            Dictionary chứa roadmap chi tiết
        """
        # Chuyển learned_knowledge thành set
        learned_set = set(learned_knowledge) if learned_knowledge else set()
        
        print(learned_knowledge)

        # Chỉ tạo roadmap cho knowledge
        knowledge_roadmap = None
        if missing_knowledge:
            knowledge_roadmap = create_roadmap(
                missing_knowledge,
                self.data_loader,
                item_type="knowledge",
                learned_items=learned_set
            )
        
        # print(f"Generated learning roadmap: {knowledge_roadmap}")

        return {
            "skills_roadmap": None,  # Không sử dụng skills nữa
            "knowledge_roadmap": knowledge_roadmap
        }
    
    def format_roadmap_for_display(self, roadmap_data: Dict) -> str:
        """
        Format roadmap thành string dễ đọc cho UI (chỉ knowledge)
        
        Args:
            roadmap_data: Kết quả từ generate_learning_roadmap
            
        Returns:
            String formatted roadmap
        """
        output = []
        
        # Format knowledge roadmap
        if roadmap_data["knowledge_roadmap"]:
            output.append("=" * 60)
            output.append("📚 KNOWLEDGE LEARNING ROADMAP")
            output.append("=" * 60)
            output.append("")
            
            kr = roadmap_data["knowledge_roadmap"]
            
            for stage in kr["roadmap"]:
                stage_num = stage["stage"]
                items = stage["items"]
                count = stage["count"]
                stage_type = stage.get("type", "path")
                
                # Xử lý 2 loại stage: scc và path
                if stage_type == "scc":
                    # SCC - các knowledge phụ thuộc lẫn nhau, học song song
                    output.append(f"Stage {stage_num}: 🔄 Learn in Parallel ({count} items)")
                else:
                    # Path - học tuần tự
                    output.append(f"Stage {stage_num}: ➡️ Learn Sequentially ({count} items)")
                
                for item in items:
                    output.append(f"  • {item}")
                
                output.append("")
        
        if not roadmap_data["knowledge_roadmap"]:
            output.append("Nothing more to learn! You're ready! 🎉")
        
        return "\n".join(output)
    
    def get_roadmap_summary(self, roadmap_data: Dict) -> Dict:
        """
        Tạo summary về roadmap (chỉ knowledge)
        
        Args:
            roadmap_data: Kết quả từ generate_learning_roadmap
            
        Returns:
            Dictionary chứa summary
        """
        summary = {
            "total_knowledge": 0,
            "total_skills": 0,  # Luôn là 0
            "knowledge_stages": 0,
            "skills_stages": 0,
            "has_cycles": False,
            "estimated_difficulty": 0.0
        }
        
        if roadmap_data["knowledge_roadmap"]:
            kr = roadmap_data["knowledge_roadmap"]
            summary["total_knowledge"] = kr["total_items"]
            summary["knowledge_stages"] = len(kr["roadmap"])
            summary["has_cycles"] = kr["has_cycles"]
        
        # Tính độ khó trung bình (chỉ knowledge)
        total_items = summary["total_knowledge"]
        if total_items > 0:
            total_difficulty = 0
            
            if roadmap_data["knowledge_roadmap"]:
                for stage in roadmap_data["knowledge_roadmap"]["roadmap"]:
                    for item in stage["items"]:
                        info = self.data_loader.get_knowledge_info(item)
                        if not info:
                            continue
                        total_difficulty += info.level
            
            summary["estimated_difficulty"] = round(total_difficulty / total_items, 2)
        
        return summary
    
    def get_next_items_to_learn(self, roadmap_data: Dict, 
                               current_stage: int = 1) -> List[str]:
        """
        Lấy danh sách items cần học ở stage tiếp theo (chỉ knowledge)
        
        Args:
            roadmap_data: Kết quả từ generate_learning_roadmap
            current_stage: Stage hiện tại (1-indexed)
            
        Returns:
            Danh sách items cần học
        """
        next_items = []
        
        if roadmap_data["knowledge_roadmap"]:
            kr = roadmap_data["knowledge_roadmap"]["roadmap"]
            if current_stage <= len(kr):
                next_items.extend(kr[current_stage - 1]["items"])
        
        return next_items
    
    def get_learning_time_estimate(self, roadmap_data: Dict, 
                                   hours_per_item: int = 20) -> Dict:
        """
        Ước tính thời gian học tập (chỉ knowledge)
        
        Args:
            roadmap_data: Kết quả từ generate_learning_roadmap
            hours_per_item: Số giờ trung bình cho mỗi item
            
        Returns:
            Dictionary chứa ước tính thời gian
        """
        summary = self.get_roadmap_summary(roadmap_data)
        total_items = summary["total_knowledge"]  # Chỉ tính knowledge
        
        # Điều chỉnh thời gian dựa trên độ khó
        difficulty_multiplier = summary["estimated_difficulty"] / 5.0
        adjusted_hours = total_items * hours_per_item * difficulty_multiplier
        
        # Nếu có parallel learning, giảm thời gian
        if summary["has_cycles"]:
            adjusted_hours *= 0.8  # Giảm 20% nhờ học song song
        
        return {
            "total_hours": round(adjusted_hours, 1),
            "total_weeks": round(adjusted_hours / 40, 1),  # 40 giờ/tuần
            "total_months": round(adjusted_hours / 160, 1),  # ~160 giờ/tháng
            "items_count": total_items,
            "difficulty_multiplier": round(difficulty_multiplier, 2)
        }
