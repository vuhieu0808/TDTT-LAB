"""
Main GUI Application sử dụng CustomTkinter
App giải quyết vấn đề thất nghiệp của sinh viên mới ra trường
"""
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import threading
from typing import List
import os
from dotenv import load_dotenv

from data_loader import DataLoader
from job_matcher import JobMatcher
from roadmap_generator import RoadmapGenerator
from ai_project_suggester import AIProjectSuggester
from selection_listbox import SelectionListbox


class StudentCareerApp(ctk.CTk):
    """Main Application Class"""
    
    def __init__(self):
        super().__init__()
        
        # Cấu hình window
        self.title("Student Career Helper - Trợ lý nghề nghiệp sinh viên")
        self.geometry("1400x900")  # Tăng kích thước window
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Load API key từ .env
        load_dotenv(".env")
        api_key = os.getenv("GEMINI_API_KEY")
        print("Loaded API Key:", "Yes" if api_key else "No")
        
        # Initialize data loader
        self.data_loader = DataLoader(data_dir=".")
        self.job_matcher = JobMatcher(self.data_loader)
        self.roadmap_generator = RoadmapGenerator(self.data_loader)
        self.ai_suggester = AIProjectSuggester(api_key=api_key) if api_key else None
        
        # Load data in background
        self.load_data_thread = threading.Thread(target=self._load_data_background)
        self.load_data_thread.start()
        
        # Create UI
        self.create_widgets()
        
    def _load_data_background(self):
        """Load dữ liệu ở background"""
        try:
            self.data_loader.load_all_data()
            print("Data loaded successfully!")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def create_widgets(self):
        """Tạo các widgets cho UI"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="🎓 Student Career Helper",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Tabview
        self.tabview = ctk.CTkTabview(self, width=1150, height=650)
        self.tabview.pack(pady=10, padx=20)
        
        # Create tabs
        self.tab1 = self.tabview.add("Tab 1: Find Suitable Jobs")
        self.tab2 = self.tabview.add("Tab 2: Generate Learning Roadmap")
        
        # Setup tab 1
        self.setup_tab1()
        
        # Setup tab 2
        self.setup_tab2()
    
    def setup_tab1(self):
        """Setup Tab 1: User chọn skills/knowledge, tìm job phù hợp"""
        
        # Main container với scrollbar
        main_container = ctk.CTkScrollableFrame(
            self.tab1,
            width=1350,
            height=750
        )
        main_container.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Top frame cho selection
        selection_frame = ctk.CTkFrame(main_container)
        selection_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        # Left side - Skills  
        skills_container = ctk.CTkFrame(selection_frame)
        skills_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            skills_container,
            text="✅ Select Your Current Skills:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Sử dụng SelectionListbox thay vì checkboxes
        self.tab1_skills_listbox = None  # Sẽ được tạo sau khi data load
        self.tab1_skills_placeholder = ctk.CTkLabel(
            skills_container,
            text="⏳ Loading skills...",
            font=ctk.CTkFont(size=12)
        )
        self.tab1_skills_placeholder.pack(fill="both", expand=True, pady=50)
        
        # Right side - Knowledge
        knowledge_container = ctk.CTkFrame(selection_frame)
        knowledge_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            knowledge_container,
            text="✅ Select Your Current Knowledge:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Sử dụng SelectionListbox thay vì checkboxes
        self.tab1_knowledge_listbox = None  # Sẽ được tạo sau khi data load
        self.tab1_knowledge_placeholder = ctk.CTkLabel(
            knowledge_container,
            text="⏳ Loading knowledge...",
            font=ctk.CTkFont(size=12)
        )
        self.tab1_knowledge_placeholder.pack(fill="both", expand=True, pady=50)
        
        # Configure grid weights
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(1, weight=1)
        selection_frame.grid_rowconfigure(0, weight=1)
        
        # Populate listboxes after data is loaded
        self.after(1000, self.populate_tab1_listboxes)
        
        # Button frame - không cần nữa vì SelectionListbox có buttons riêng
        # button_frame = ctk.CTkFrame(main_container)
        # button_frame.pack(pady=10)
        
        # Action buttons frame
        action_buttons_frame = ctk.CTkFrame(main_container)
        action_buttons_frame.pack(pady=10)
        
        # Find job button
        find_job_btn = ctk.CTkButton(
            action_buttons_frame,
            text="🔍 Find Suitable Jobs",
            command=self.find_suitable_jobs,
            width=220,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        find_job_btn.grid(row=0, column=0, padx=10)
        
        # # Suggest project button
        # suggest_project_tab1_btn = ctk.CTkButton(
        #     action_buttons_frame,
        #     text="💡 Suggest Projects",
        #     command=self.suggest_project_tab1,
        #     width=220,
        #     height=45,
        #     font=ctk.CTkFont(size=16, weight="bold")
        # )
        # suggest_project_tab1_btn.grid(row=0, column=1, padx=10)
        
        # Lưu kết quả tìm job để dùng cho suggest project
        self.tab1_job_results = None
        
        # Output frame - Mở rộng
        output_frame = ctk.CTkFrame(main_container)
        output_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        ctk.CTkLabel(
            output_frame,
            text="📊 Results:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        self.tab1_output = ctk.CTkTextbox(output_frame, width=1300, height=350, wrap="word")
        self.tab1_output.pack(padx=10, pady=5, fill="both", expand=True)
    
    def populate_tab1_listboxes(self):
        """Populate SelectionListbox widgets với data từ data_loader"""
        # Wait for data to be loaded
        if not self.data_loader.skills_data or not self.data_loader.knowledge_data:
            self.after(500, self.populate_tab1_listboxes)
            return
        
        # Get expanded skills và knowledge
        expanded_skills, expanded_knowledge = self.data_loader.get_expanded_skills_and_knowledge()
        
        if not expanded_skills or not expanded_knowledge:
            print(f"Warning: Empty expanded data")
            self.after(500, self.populate_tab1_listboxes)
            return
        
        print(f"Creating Tab 1 listboxes: {len(expanded_skills)} skills, {len(expanded_knowledge)} knowledge")
        
        # Destroy placeholders
        self.tab1_skills_placeholder.destroy()
        self.tab1_knowledge_placeholder.destroy()
        
        # Create SelectionListbox widgets
        self.tab1_skills_listbox = SelectionListbox(
            self.tab1_skills_placeholder.master,
            items=expanded_skills
        )
        self.tab1_skills_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab1_knowledge_listbox = SelectionListbox(
            self.tab1_knowledge_placeholder.master,
            items=expanded_knowledge
        )
        self.tab1_knowledge_listbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    def populate_tab2_listboxes(self):
        """Populate SelectionListbox widgets cho Tab 2 với data từ data_loader"""
        # Wait for data to be loaded
        if not self.data_loader.skills_data or not self.data_loader.knowledge_data:
            self.after(500, self.populate_tab2_listboxes)
            return
        
        # Get expanded skills và knowledge
        expanded_skills, expanded_knowledge = self.data_loader.get_expanded_skills_and_knowledge()
        
        if not expanded_skills or not expanded_knowledge:
            print(f"Warning: Empty expanded data")
            self.after(500, self.populate_tab2_listboxes)
            return
        
        print(f"Creating Tab 2 listboxes: {len(expanded_skills)} skills, {len(expanded_knowledge)} knowledge")
        
        # Destroy placeholders
        self.tab2_skills_placeholder.destroy()
        self.tab2_knowledge_placeholder.destroy()
        
        # Create SelectionListbox widgets
        self.tab2_skills_listbox = SelectionListbox(
            self.tab2_skills_placeholder.master,
            items=expanded_skills
        )
        self.tab2_skills_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab2_knowledge_listbox = SelectionListbox(
            self.tab2_knowledge_placeholder.master,
            items=expanded_knowledge
        )
        self.tab2_knowledge_listbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Xóa các methods filter và select_all cũ - không cần nữa với SelectionListbox
    
    def setup_tab2(self):
        """Setup Tab 2: User chọn job target và skills/knowledge, tạo roadmap"""
        
        # Main container với scrollbar
        main_container = ctk.CTkScrollableFrame(
            self.tab2,
            width=1350,
            height=750
        )
        main_container.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Top frame - Job selection với autocomplete
        job_frame = ctk.CTkFrame(main_container)
        job_frame.pack(pady=5, padx=5, fill="x")
        
        # Lưu label để tính toán vị trí dropdown
        self.tab2_job_label = ctk.CTkLabel(
            job_frame,
            text="🎯 Target Job Title:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.tab2_job_label.pack(side="left", padx=10, pady=5)
        
        # Container cho entry và dropdown
        job_input_container = ctk.CTkFrame(job_frame, fg_color="transparent")
        job_input_container.pack(side="left", padx=10, pady=5)
        
        self.tab2_job_entry = ctk.CTkEntry(
            job_input_container,
            width=500,
            height=35,
            placeholder_text="Type to search job... (e.g., cloud, engineer, developer)"
        )
        self.tab2_job_entry.pack()
        self.tab2_job_entry.bind("<KeyRelease>", self.on_job_entry_change)
        self.tab2_job_entry.bind("<FocusOut>", lambda e: self.after(200, self.hide_job_suggestions))
        self.tab2_job_entry.bind("<Escape>", lambda e: self.hide_job_suggestions())
        
        # Dropdown frame cho autocomplete suggestions - dùng place để đè lên trên
        self.job_suggestions_frame = ctk.CTkScrollableFrame(
            main_container,  # Đổi parent thành main_container để có thể đè lên các phần tử khác
            width=500,
            height=0,  # Ẩn ban đầu
            fg_color=("#E0E0E0", "#2B2B2B"),
            border_width=2,
            border_color=("gray70", "gray30")
        )
        # Sử dụng place để dropdown đè lên trên, không pack
        
        # List để lưu suggestion buttons
        self.job_suggestion_buttons = []
        
        # Selection frame cho Skills và Knowledge
        selection_frame = ctk.CTkFrame(main_container)
        selection_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        # Left side - Skills
        skills_container = ctk.CTkFrame(selection_frame)
        skills_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            skills_container,
            text="✅ Select Your Current Skills:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Sử dụng SelectionListbox
        self.tab2_skills_listbox = None
        self.tab2_skills_placeholder = ctk.CTkLabel(
            skills_container,
            text="⏳ Loading skills...",
            font=ctk.CTkFont(size=12)
        )
        self.tab2_skills_placeholder.pack(fill="both", expand=True, pady=50)
        
        # Right side - Knowledge
        knowledge_container = ctk.CTkFrame(selection_frame)
        knowledge_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            knowledge_container,
            text="✅ Select Your Current Knowledge:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Sử dụng SelectionListbox
        self.tab2_knowledge_listbox = None
        self.tab2_knowledge_placeholder = ctk.CTkLabel(
            knowledge_container,
            text="⏳ Loading knowledge...",
            font=ctk.CTkFont(size=12)
        )
        self.tab2_knowledge_placeholder.pack(fill="both", expand=True, pady=50)
        
        # Configure grid weights
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(1, weight=1)
        selection_frame.grid_rowconfigure(0, weight=1)
        
        # Populate listboxes after data is loaded
        self.after(1000, self.populate_tab2_listboxes)
        
        # Main action buttons
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(pady=10)
        
        generate_roadmap_btn = ctk.CTkButton(
            button_frame,
            text="🗺️ Generate Roadmap",
            command=self.generate_roadmap,
            width=220,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        generate_roadmap_btn.grid(row=0, column=0, padx=10)
        
        suggest_project_btn = ctk.CTkButton(
            button_frame,
            text="💡 Suggest Projects",
            command=self.suggest_project,
            width=220,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        suggest_project_btn.grid(row=0, column=1, padx=10)
        
        # Output frame - Mở rộng
        output_frame = ctk.CTkFrame(main_container)
        output_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        ctk.CTkLabel(
            output_frame,
            text="📊 Results:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        self.tab2_output = ctk.CTkTextbox(output_frame, width=1300, height=350, wrap="word")
        self.tab2_output.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Lưu roadmap data để dùng cho suggest project
        self.current_roadmap_data = None
        self.current_missing_items = None
    
    
    def on_job_entry_change(self, event=None):
        """Xử lý autocomplete khi user gõ vào job entry"""
        search_text = self.tab2_job_entry.get().strip().lower()
        
        # Clear old suggestions
        for btn in self.job_suggestion_buttons:
            btn.destroy()
        self.job_suggestion_buttons.clear()
        
        # Nếu text quá ngắn hoặc rỗng, ẩn dropdown
        if len(search_text) < 2:
            self.job_suggestions_frame.place_forget()
            return
        
        # Tìm matching jobs (bao gồm cả other_names)
        matching_jobs = []
        seen_canonical = set()  # Để tránh duplicate canonical names
        
        for job in self.data_loader.jobs_data:
            canonical_name = job["name"]
            job_name_lower = canonical_name.lower()
            
            # Check trong tên chính
            if search_text in job_name_lower:
                if canonical_name not in seen_canonical:
                    matching_jobs.append((canonical_name, canonical_name))
                    seen_canonical.add(canonical_name)
            
            # Check trong other_names
            if "other_name" in job:
                for other_name in job["other_name"]:
                    if search_text in other_name.lower():
                        if canonical_name not in seen_canonical:
                            # Format: "devops engineer → cloud DevOps engineer"
                            display_name = f"{other_name} → {canonical_name}"
                            matching_jobs.append((display_name, canonical_name))
                            seen_canonical.add(canonical_name)
                        break
        
        # Limit số lượng suggestions
        matching_jobs = matching_jobs[:10]  # Max 10 suggestions
        
        # Nếu không có match, ẩn dropdown
        if not matching_jobs:
            self.job_suggestions_frame.place_forget()
            return
        
        # Hiển thị suggestions
        for display_name, canonical_name in matching_jobs:
            btn = ctk.CTkButton(
                self.job_suggestions_frame,
                text=display_name,
                command=lambda cn=canonical_name: self.select_job_suggestion(cn),
                width=480,
                height=30,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "gray25"),
                hover_color=("gray75", "gray35"),
                anchor="w"
            )
            btn.pack(pady=2, padx=5)
            self.job_suggestion_buttons.append(btn)
        
        # Show dropdown với height phù hợp - dùng place để đè lên trên
        dropdown_height = min(len(matching_jobs) * 35, 300)  # Max 300px
        
        # Configure kích thước trước
        self.job_suggestions_frame.configure(width=500, height=dropdown_height)
        
        # Tính toán vị trí của dropdown (dưới entry box)
        # Lấy width của label "Target Job Title:" và padding
        label_width = self.tab2_job_label.winfo_width()
        
        entry_x = self.tab2_job_entry.winfo_x()
        entry_y = self.tab2_job_entry.winfo_y() + self.tab2_job_entry.winfo_height()
        
        # Place dropdown đè lên trên các elements khác (chỉ truyền x, y)
        self.job_suggestions_frame.place(
            x=entry_x + label_width,  # Cộng thêm width của label và padding
            y=entry_y + 15   # offset để xuống dưới entry
        )
        self.job_suggestions_frame.lift()  # Đưa lên trên cùng
    
    def select_job_suggestion(self, canonical_job_name: str):
        """Chọn một job từ suggestion dropdown"""
        self.tab2_job_entry.delete(0, "end")
        self.tab2_job_entry.insert(0, canonical_job_name)
        
        # Hide dropdown
        self.hide_job_suggestions()
    
    def hide_job_suggestions(self):
        """Ẩn job suggestions dropdown"""
        self.job_suggestions_frame.place_forget()
        
        # Clear suggestion buttons
        for btn in self.job_suggestion_buttons:
            btn.destroy()
        self.job_suggestion_buttons.clear()
    
    def find_suitable_jobs(self):
        """Xử lý tìm job phù hợp (Tab 1)"""
        # Check if listboxes exist
        if not self.tab1_skills_listbox or not self.tab1_knowledge_listbox:
            messagebox.showwarning("Warning", "Please wait for data to load!")
            return
        
        # Get selected canonical names from SelectionListbox
        user_skills = self.tab1_skills_listbox.get_selected_canonical()
        user_knowledge = self.tab1_knowledge_listbox.get_selected_canonical()
        
        if not user_skills and not user_knowledge:
            messagebox.showwarning("Warning", "Please select at least one skill or knowledge!")
            return
        
        print("User Skills Selected (canonical):", user_skills)
        print("User Knowledge Selected (canonical):", user_knowledge)
        
        # Lưu user knowledge để dùng cho suggest project
        self.tab1_user_knowledge = user_knowledge
        
        # Clear output
        self.tab1_output.delete("1.0", "end")
        self.tab1_output.insert("1.0", f"Searching with {len(user_skills)} skills and {len(user_knowledge)} knowledge...\n")
        self.update()
        
        # Find jobs
        try:
            results = self.job_matcher.find_suitable_jobs(
                user_skills,
                user_knowledge,
                min_score=5.0,  # Điểm tối thiểu rất thấp
                top_n=15  # Hiển thị nhiều kết quả hơn
            )
            
            # Lưu kết quả để dùng cho suggest project
            self.tab1_job_results = results
            
            # Display results
            self.tab1_output.delete("1.0", "end")
            
            if not results:
                self.tab1_output.insert("end", "❌ No suitable jobs found with selected skills.\n\n")
                self.tab1_output.insert("end", "💡 Suggestions:\n")
                self.tab1_output.insert("end", "  • Try selecting more related skills/knowledge\n")
                self.tab1_output.insert("end", "  • Review your selected items\n")
            else:
                self.tab1_output.insert("end", f"🎯 Found {len(results)} suitable jobs:\n")
                self.tab1_output.insert("end", f"📌 You selected: {len(user_skills)} skills, {len(user_knowledge)} knowledge\n\n")
                
                for idx, job in enumerate(results, 1):
                    output = f"{'='*70}\n"
                    output += f"{idx}. {job['job_name']} - Score: {job['total_score']:.1f}%\n"
                    output += f"{'='*70}\n"
                    output += f"   Required: {job['required_score']:.1f}% | Optional: {job['optional_score']:.1f}%\n\n"
                    
                    # Matched requirements (show what user has)
                    matched = job['matched']
                    total_matched = (len(matched['required_skills']) + len(matched['required_knowledge']) + 
                                   len(matched['optional_skills']) + len(matched['optional_knowledge']))
                    
                    output += f"   ✅ You Have ({total_matched} items):\n"
                    if matched['required_skills']:
                        output += f"      Skills (required): {', '.join(matched['required_skills'][:3])}\n"
                    if matched['required_knowledge']:
                        output += f"      Knowledge (required): {', '.join(matched['required_knowledge'][:3])}\n"
                    if matched['optional_skills'] or matched['optional_knowledge']:
                        output += f"      Bonus: {len(matched['optional_skills']) + len(matched['optional_knowledge'])} optional items\n"
                    output += "\n"
                    
                    # Missing requirements
                    missing = job['missing']
                    total_missing = (len(missing['required_skills']) + len(missing['required_knowledge']) + 
                                   len(missing['optional_skills']) + len(missing['optional_knowledge']))
                    
                    if missing['required_skills'] or missing['required_knowledge']:
                        output += f"   ❌ Missing ({total_missing} items):\n"
                        if missing['required_skills']:
                            output += f"      Skills (REQUIRED): {', '.join(missing['required_skills'][:5])}\n"
                        if missing['required_knowledge']:
                            output += f"      Knowledge (REQUIRED): {', '.join(missing['required_knowledge'][:5])}\n"
                        if missing['optional_skills'] or missing['optional_knowledge']:
                            optional_count = len(missing['optional_skills']) + len(missing['optional_knowledge'])
                            output += f"      Optional: {optional_count} items (can be added)\n"
                    
                    output += "\n\n"
                    
                    self.tab1_output.insert("end", output)
            
            # Scroll to top để hiển thị kết quả đầu tiên
            self.tab1_output.see("1.0")
            
        except Exception as e:
            self.tab1_output.delete("1.0", "end")
            self.tab1_output.insert("end", f"❌ Error: {str(e)}\n\n")
            import traceback
            self.tab1_output.insert("end", traceback.format_exc())
    
    def generate_roadmap(self):
        """Xử lý tạo roadmap (Tab 2)"""
        # Get input
        job_name = self.tab2_job_entry.get().strip()
        
        # Map job name về canonical name nếu cần
        job_name_canonical = self.data_loader.get_canonical_job_name(job_name)
        
        # Get selected items từ listboxes (đã là canonical names)
        user_skills = self.tab2_skills_listbox.get_selected_canonical()
        user_knowledge = self.tab2_knowledge_listbox.get_selected_canonical()
        
        if not job_name:
            messagebox.showwarning("Warning", "Please enter a job title!")
            return
        
        # Remove duplicates (nếu có)
        user_skills = list(set(user_skills))
        user_knowledge = list(set(user_knowledge))
        
        # Clear output
        self.tab2_output.delete("1.0", "end")
        self.tab2_output.insert("1.0", f"Analyzing for job '{job_name_canonical}'...\n")
        self.tab2_output.insert("end", f"With {len(user_skills)} skills and {len(user_knowledge)} knowledge you have...\n")
        self.update()
        
        try:
            # Get missing requirements (sử dụng canonical job name)
            missing_info = self.job_matcher.get_missing_requirements(
                job_name_canonical,
                user_skills,
                user_knowledge
            )
            
            if not missing_info.get("found"):
                self.tab2_output.delete("1.0", "end")
                self.tab2_output.insert("end", f"Error: {missing_info.get('error', 'Job not found')}")
                return
            
            # Generate roadmap CHỈ CHO ESSENTIAL (REQUIRED) KNOWLEDGE
            missing = missing_info["missing"]
            
            # CHỈ LẤY REQUIRED KNOWLEDGE - KHÔNG LẤY OPTIONAL
            missing_required_knowledge = missing["required_knowledge"]
            missing_optional_knowledge = missing["optional_knowledge"]
            
            # Lưu để dùng cho suggest project (chỉ required)
            self.current_missing_items = {
                "required_knowledge": missing_required_knowledge,
                "optional_knowledge": missing_optional_knowledge  # Lưu riêng để hiển thị
            }
            
            # Kiểm tra xem có cần học gì không
            if not missing_required_knowledge:
                self.tab2_output.delete("1.0", "end")
                output = "🎉 Congratulations! You meet all REQUIRED requirements for this job!\n\n"
                
                # Hiển thị optional knowledge nếu có
                if missing_optional_knowledge:
                    output += f"💡 OPTIONAL knowledge you can learn ({len(missing_optional_knowledge)} items):\n"
                    output += "   (These are not required but will be an advantage)\n\n"
                    for idx, knowledge in enumerate(missing_optional_knowledge, 1):
                        output += f"   {idx}. {knowledge}\n"
                
                self.tab2_output.insert("end", output)
                return
            
            # TẠO ROADMAP CHỈ VỚI REQUIRED KNOWLEDGE
            roadmap_data = self.roadmap_generator.generate_learning_roadmap(
                [],  # Không dùng skills
                missing_required_knowledge,  # CHỈ REQUIRED KNOWLEDGE
                learned_knowledge=user_knowledge  # Knowledge user đã có
            )
            
            self.current_roadmap_data = roadmap_data
            
            # Display roadmap
            self.tab2_output.delete("1.0", "end")
            
            # Header (hiển thị canonical job name)
            output = f"🎯 LEARNING ROADMAP FOR: {job_name_canonical}\n"
            output += f"{'='*70}\n\n"
            
            # Summary (chỉ required knowledge)
            summary = self.roadmap_generator.get_roadmap_summary(roadmap_data)
            output += f"📊 REQUIRED KNOWLEDGE Overview:\n"
            output += f"   • Total knowledge to learn: {summary['total_knowledge']}\n"
            # output += f"   • Độ khó trung bình: {summary['estimated_difficulty']}/10\n"
            
            # Time estimate
            # time_est = self.roadmap_generator.get_learning_time_estimate(roadmap_data)
            # output += f"   • Thời gian ước tính: {time_est['total_months']} tháng ({time_est['total_hours']} giờ)\n\n"
            
            self.tab2_output.insert("end", output)
            
            # Detailed roadmap
            formatted_roadmap = self.roadmap_generator.format_roadmap_for_display(roadmap_data)
            self.tab2_output.insert("end", formatted_roadmap)
            
            # HIỂN thị OPTIONAL KNOWLEDGE RIÊNG BIỆT (không trong roadmap)
            if missing_optional_knowledge:
                output = "\n" + "="*70 + "\n"
                output += f"💡 OPTIONAL KNOWLEDGE - {len(missing_optional_knowledge)} items\n"
                output += "="*70 + "\n"
                output += "These knowledge are NOT REQUIRED but will be an advantage:\n\n"
                
                for idx, knowledge in enumerate(missing_optional_knowledge, 1):
                    info = self.data_loader.get_knowledge_info(knowledge)
                    level = info.get("level", 5)
                    output += f"  {idx}. {knowledge} [Độ khó: {level}/10]\n"
                    if info.get("detailed"):
                        output += f"      Chi tiết: {', '.join(info['detailed'][:2])}\n"
                
                output += "\n💭 You can learn these after completing the main roadmap.\n"
                self.tab2_output.insert("end", output)
            
            # Scroll to top để hiển thị từ đầu
            self.tab2_output.see("1.0")
            
        except Exception as e:
            self.tab2_output.delete("1.0", "end")
            self.tab2_output.insert("end", f"Error: {str(e)}\n{type(e).__name__}")
    
    def suggest_project(self):
        """Đề xuất project sử dụng Google Gemini AI (Tab 2)"""
        # if not self.current_missing_items:
        #     messagebox.showwarning("Cảnh báo", "Vui lòng tạo roadmap trước khi đề xuất project!")
        #     return
        
        if not self.ai_suggester:
            messagebox.showwarning(
                "Warning",
                "GEMINI_API_KEY not found in .env file!\n\n" +
                "Please add GEMINI_API_KEY to .env file"
            )
            return
        
        # Clear output và hiển thị loading
        self.tab2_output.delete("1.0", "end")
        self.tab2_output.insert("end", "🤖 Generating project suggestions...\n")
        self.update()
        
        # Lấy tên job và map về canonical name
        job_name = self.tab2_job_entry.get().strip()
        job_name_canonical = self.data_loader.get_canonical_job_name(job_name)
        
        if not job_name:
            messagebox.showwarning("Warning", "Please enter a job title!")
            return
        
        # Lấy user knowledge từ listbox (đã là canonical names)
        user_knowledge = self.tab2_knowledge_listbox.get_selected_canonical()
        user_knowledge = list(set(user_knowledge))  # Remove duplicates
        
        # Run in thread để không block UI
        def suggest_in_thread():
            try:
                # Lấy job info từ data_loader (sử dụng canonical name)
                job_info = self.data_loader.get_job_by_name(job_name_canonical)
                
                if not job_info:
                    self.tab2_output.delete("1.0", "end")
                    self.tab2_output.insert("end", f"❌ Job information not found: {job_name_canonical}")
                    return
                
                # Gọi AI với job_info và student_knowledge
                project_data = self.ai_suggester.suggest_project(
                    job_info,
                    user_knowledge
                )
                
                formatted = self.ai_suggester.format_project_for_display(project_data)
                
                self.tab2_output.delete("1.0", "end")
                self.tab2_output.insert("end", formatted)
                
                # Scroll to top để hiển thị từ đầu
                self.tab2_output.see("1.0")
                
            except Exception as e:
                self.tab2_output.delete("1.0", "end")
                self.tab2_output.insert("end", f"Error suggesting projects: {str(e)}")
        
        thread = threading.Thread(target=suggest_in_thread)
        thread.start()
    
    def suggest_project_tab1(self):
        """Đề xuất project cho các jobs đã tìm được (Tab 1)"""
        if not hasattr(self, 'tab1_job_results') or not self.tab1_job_results:
            messagebox.showwarning("Warning", "Please find suitable jobs first!")
            return
        
        if not self.ai_suggester:
            messagebox.showwarning(
                "Warning",
                "GEMINI_API_KEY not found in .env file!\n\n" +
                "Please add GEMINI_API_KEY to .env file"
            )
            return
        
        # Clear output và hiển thị loading
        self.tab1_output.delete("1.0", "end")
        self.tab1_output.insert("end", "🤖 Generating project suggestions for jobs...\n\n")
        self.update()
        
        # Lấy top 3 jobs để suggest project
        top_jobs = self.tab1_job_results[:3]
        
        def suggest_in_thread():
            try:
                output_text = ""
                
                for idx, job_result in enumerate(top_jobs, 1):
                    job_name = job_result['job_name']
                    
                    # Lấy thông tin job từ data_loader
                    job_info = self.data_loader.get_job_by_name(job_name)
                    
                    if not job_info:
                        output_text += f"\n❌ Job information not found: {job_name}\n\n"
                        continue
                    
                    output_text += f"{'='*70}\n"
                    output_text += f"JOB {idx}: {job_name}\n"
                    output_text += f"{'='*70}\n\n"
                    
                    # Gọi AI để suggest project
                    project_data = self.ai_suggester.suggest_project(
                        job_info,
                        self.tab1_user_knowledge
                    )
                    
                    if "error" in project_data:
                        output_text += f"❌ Error: {project_data['error']}\n\n"
                    else:
                        # Format project suggestions
                        formatted = self.ai_suggester.format_project_for_display(project_data)
                        output_text += formatted + "\n\n"
                
                # Hiển thị kết quả
                self.tab1_output.delete("1.0", "end")
                self.tab1_output.insert("end", output_text)
                self.tab1_output.see("1.0")
                
            except Exception as e:
                self.tab1_output.delete("1.0", "end")
                self.tab1_output.insert("end", f"❌ Error suggesting projects: {str(e)}")
        
        thread = threading.Thread(target=suggest_in_thread)
        thread.start()

def main():
    """Main function"""
    app = StudentCareerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
