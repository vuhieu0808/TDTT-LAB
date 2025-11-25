"""
Main GUI Application sử dụng CustomTkinter
App giải quyết vấn đề thất nghiệp của sinh viên mới ra trường
Simplified GUI with shared Profile Sidebar
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import os
from dotenv import load_dotenv
from typing import List, Dict, Set, Tuple

from data_loader import DataLoader
from job_matcher import JobMatcher
from roadmap_generator import RoadmapGenerator
from ai_project_suggester import AIProjectSuggester
from selection_listbox import SelectionListbox


class FindJobsTab(ctk.CTkFrame):
    """Tab 1: Find Suitable Jobs"""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.pack(fill="both", expand=True)
        self.setup_ui()
        
    def setup_ui(self):
        # Top Control Panel
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(pady=10, padx=10, fill="x")
        
        find_btn = ctk.CTkButton(
            controls_frame,
            text="🔍 Find Jobs Matching Profile",
            command=self.find_suitable_jobs,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        find_btn.pack(fill="x")
        
        # Results Area
        self.output = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.output.pack(pady=10, padx=10, fill="both", expand=True)

    def find_suitable_jobs(self):
        user_skills, user_knowledge = self.app.get_user_profile()
        
        if not user_skills and not user_knowledge:
            messagebox.showwarning("Profile Empty", "Please select at least one skill or knowledge in the sidebar.")
            return
            
        self.output.delete("1.0", "end")
        self.output.insert("1.0", f"🔎 Searching jobs for profile: {len(user_skills)} skills, {len(user_knowledge)} knowledge...\n\n")
        self.update()
        
        try:
            results = self.app.job_matcher.find_suitable_jobs(
                user_skills, user_knowledge, min_score=5.0, top_n=15
            )
            
            if not results:
                self.output.insert("end", "❌ No suitable jobs found.\nTry adding more skills or knowledge to your profile.")
                return

            for idx, job in enumerate(results, 1):
                self._display_job_result(idx, job)
                
        except Exception as e:
            self.output.insert("end", f"❌ Error: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def _display_job_result(self, idx, job):
        matched = job['matched']
        missing = job['missing']
        
        # Calculate counts
        n_matched = len(matched['required_skills']) + len(matched['required_knowledge']) + \
                   len(matched['optional_skills']) + len(matched['optional_knowledge'])
        
        text = f"{'='*60}\n"
        text += f"{idx}. {job['job_name']} (Match: {job['total_score']:.1f}%)\n"
        text += f"{'='*60}\n"
        text += f"   ✅ You have {n_matched} matching items\n"
        
        # Show missing required
        missing_req = missing['required_skills'] + missing['required_knowledge']
        if missing_req:
            text += f"   ⚠️ Missing Required: {', '.join(missing_req[:5])}"
            if len(missing_req) > 5: text += "..."
            text += "\n"
            
        text += "\n"
        self.output.insert("end", text)


class RoadmapTab(ctk.CTkFrame):
    """Tab 2: Roadmap & Projects"""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.pack(fill="both", expand=True)
        self.job_suggestion_buttons = []
        self.setup_ui()
        
    def setup_ui(self):
        # Input Area
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(input_frame, text="Target Job:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        self.job_entry = ctk.CTkEntry(input_frame, placeholder_text="Type job title (e.g. Python Developer)...")
        self.job_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.job_entry.bind("<KeyRelease>", self.on_job_entry_change)
        self.job_entry.bind("<FocusOut>", lambda e: self.after(200, self.hide_suggestions))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(btn_frame, text="🗺️ Generate Roadmap", command=self.generate_roadmap).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="💡 AI Project Ideas", command=self.suggest_project, fg_color="#2B8256", hover_color="#1E5E3D").pack(side="left", fill="x", expand=True, padx=5)

        # Suggestions Dropdown (Floating)
        self.suggestions_frame = ctk.CTkScrollableFrame(self, height=0, fg_color="gray25")
        
        # Output
        self.output = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.output.pack(pady=10, padx=10, fill="both", expand=True)

    def on_job_entry_change(self, event=None):
        text = self.job_entry.get().strip().lower()
        self.hide_suggestions()
        
        if len(text) < 2: return
        
        matches = []
        seen = set()
        
        for job in self.app.data_loader.jobs_data:
            c_name = job["name"]
            if text in c_name.lower() and c_name not in seen:
                matches.append((c_name, c_name))
                seen.add(c_name)
            
            if "other_name" in job:
                for other in job["other_name"]:
                    if text in other.lower() and c_name not in seen:
                        matches.append((f"{other} -> {c_name}", c_name))
                        seen.add(c_name)
                        break
        
        if not matches: return
        
        # Show suggestions
        self.suggestions_frame.place(x=100, y=55, width=400, height=min(len(matches)*35, 200))
        self.suggestions_frame.lift()
        
        for display, val in matches[:8]:
            btn = ctk.CTkButton(
                self.suggestions_frame, 
                text=display, 
                anchor="w",
                fg_color="transparent",
                command=lambda v=val: self.select_suggestion(v)
            )
            btn.pack(fill="x", pady=1)
            self.job_suggestion_buttons.append(btn)

    def hide_suggestions(self):
        self.suggestions_frame.place_forget()
        for btn in self.job_suggestion_buttons: btn.destroy()
        self.job_suggestion_buttons.clear()

    def select_suggestion(self, value):
        self.job_entry.delete(0, "end")
        self.job_entry.insert(0, value)
        self.hide_suggestions()

    def generate_roadmap(self):
        job_name = self.job_entry.get().strip()
        if not job_name:
            messagebox.showwarning("Input Required", "Please enter a target job title.")
            return

        user_skills, user_knowledge = self.app.get_user_profile()
        canonical_name = self.app.data_loader.get_canonical_job_name(job_name)
        
        self.output.delete("1.0", "end")
        self.output.insert("1.0", f"📊 Analyzing gap for '{canonical_name}'...\n")
        
        try:
            missing_info = self.app.job_matcher.get_missing_requirements(
                canonical_name, user_skills, user_knowledge
            )
            
            if not missing_info.get("found"):
                self.output.insert("end", f"❌ Job '{job_name}' not found in database.")
                return

            missing = missing_info["missing"]
            req_knowledge = missing["required_knowledge"]
            
            if not req_knowledge:
                self.output.insert("end", "\n🎉 You have all required knowledge for this job!\n")
                if missing["optional_knowledge"]:
                    self.output.insert("end", "\n💡 Optional improvements:\n")
                    for k in missing["optional_knowledge"]: self.output.insert("end", f" - {k}\n")
                return

            # Generate Roadmap
            roadmap = self.app.roadmap_generator.generate_learning_roadmap(
                [], req_knowledge, learned_knowledge=user_knowledge
            )
            
            formatted = self.app.roadmap_generator.format_roadmap_for_display(roadmap)
            self.output.insert("end", f"\n{formatted}")
            
        except Exception as e:
            self.output.insert("end", f"❌ Error: {str(e)}")

    def suggest_project(self):
        if not self.app.ai_suggester:
            messagebox.showerror("Error", "AI Module not initialized (Check API Key).")
            return
            
        job_name = self.job_entry.get().strip()
        if not job_name: return
        
        canonical_name = self.app.data_loader.get_canonical_job_name(job_name)
        _, user_knowledge = self.app.get_user_profile()
        
        self.output.delete("1.0", "end")
        self.output.insert("1.0", "🤖 Asking Gemini AI for project ideas...\n")
        self.update()
        
        def _run():
            try:
                job_info = self.app.data_loader.get_job_by_name(canonical_name)
                if not job_info:
                    self.output.insert("end", "❌ Job not found.")
                    return
                    
                result = self.app.ai_suggester.suggest_project(job_info, list(set(user_knowledge)))
                text = self.app.ai_suggester.format_project_for_display(result)
                
                self.output.delete("1.0", "end")
                self.output.insert("end", text)
            except Exception as e:
                self.output.insert("end", f"❌ AI Error: {str(e)}")
                
        threading.Thread(target=_run).start()


class StudentCareerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Career Helper")
        self.geometry("1300x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Load Data & API
        load_dotenv(".env")
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Init Logic Modules
        self.data_loader = DataLoader(data_dir=".")
        self.job_matcher = JobMatcher(self.data_loader)
        self.roadmap_generator = RoadmapGenerator(self.data_loader)
        self.ai_suggester = AIProjectSuggester(api_key=self.api_key) if self.api_key else None
        
        # UI Components
        self.skills_listbox = None
        self.knowledge_listbox = None
        
        self._setup_layout()
        
        # Async Data Load
        threading.Thread(target=self._load_data).start()

    def _setup_layout(self):
        # 2 Columns: Sidebar (Profile) | Main (Tabs)
        self.grid_columnconfigure(0, weight=0, minsize=300) # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1) # Main expands
        self.grid_rowconfigure(0, weight=1)
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Enforce width
        
        ctk.CTkLabel(self.sidebar, text="👤 YOUR PROFILE", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        # Skills
        ctk.CTkLabel(self.sidebar, text="Skills", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        self.skills_container = ctk.CTkScrollableFrame(self.sidebar)
        self.skills_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.skills_loading = ctk.CTkLabel(self.skills_container, text="Loading...")
        self.skills_loading.pack(pady=20)
        
        # Knowledge
        ctk.CTkLabel(self.sidebar, text="Knowledge", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        self.knowledge_container = ctk.CTkScrollableFrame(self.sidebar)
        self.knowledge_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.knowledge_loading = ctk.CTkLabel(self.knowledge_container, text="Loading...")
        self.knowledge_loading.pack(pady=20)
        
        # --- Main Area ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.tab1 = self.tab_view.add("Find Jobs")
        self.tab2 = self.tab_view.add("Roadmap & Projects")
        
        self.find_jobs_tab = FindJobsTab(self.tab1, self)
        self.roadmap_tab = RoadmapTab(self.tab2, self)

    def _load_data(self):
        try:
            time.sleep(0.5) 
            self.after(0, self._populate_sidebar)
        except Exception as e:
            print(f"Data load error: {e}")

    def _populate_sidebar(self):
        knowledge: List[Tuple[str, str]] = []
        skills: List[Tuple[str, str]] = []

        # Clear loading
        self.skills_loading.destroy()
        self.knowledge_loading.destroy()
        
        # Create Listboxes
        self.skills_listbox = SelectionListbox(self.skills_container, items=skills)
        self.skills_listbox.pack(fill="both", expand=True)
        
        self.knowledge_listbox = SelectionListbox(self.knowledge_container, items=knowledge)
        self.knowledge_listbox.pack(fill="both", expand=True)

    def get_user_profile(self):
        """Returns (selected_skills, selected_knowledge) as canonical names"""
        if not self.skills_listbox or not self.knowledge_listbox:
            return [], []
        return (
            self.skills_listbox.get_selected_canonical(),
            self.knowledge_listbox.get_selected_canonical()
        )

def main():
    app = StudentCareerApp()
    app.mainloop()

if __name__ == "__main__":
    main()