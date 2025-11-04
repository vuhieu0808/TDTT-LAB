import customtkinter as ctk
from tkinter import messagebox, Listbox, END
import json
import os

# ===================================================================
# PHẦN 1: LOAD DỮ LIỆU TỪ JSON FILES
# ===================================================================

# Đường dẫn tới các file JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DB_PATH = os.path.join(BASE_DIR, 'assets', 'skills_database.json')
JOBS_DB_PATH = os.path.join(BASE_DIR, 'assets', 'it_jobs_database.json')
MAPPING_PATH = os.path.join(BASE_DIR, 'assets', 'job_skill_mapping.json')

# Load dữ liệu
with open(SKILLS_DB_PATH, 'r', encoding='utf-8') as f:
    skills_database = json.load(f)

with open(JOBS_DB_PATH, 'r', encoding='utf-8') as f:
    jobs_database = json.load(f)

with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
    mapping_database = json.load(f)

# Tạo dictionary mapping từ skill_id sang skill_name
SKILL_ID_TO_NAME = {}
SKILL_NAME_TO_ID = {}
for category in skills_database['skill_categories']:
    for skill in category['skills']:
        SKILL_ID_TO_NAME[skill['id']] = skill['name']
        SKILL_NAME_TO_ID[skill['name']] = skill['id']

# Tạo dictionary mapping từ job_id sang job info
JOB_ID_TO_INFO = {}
JOB_TITLE_TO_ID = {}
for category in jobs_database['job_categories']:
    for job in category['jobs']:
        JOB_ID_TO_INFO[job['id']] = job
        JOB_TITLE_TO_ID[job['title_vi']] = job['id']

# Tạo danh sách tất cả skills và jobs để hiển thị
ALL_SKILLS = sorted([skill['name'] for cat in skills_database['skill_categories'] for skill in cat['skills']])
ALL_CAREERS = sorted([job['title_vi'] for cat in jobs_database['job_categories'] for job in cat['jobs']])

# ===================================================================
# PHẦN 2: CÁC HÀM LOGIC CỐT LÕI
# ===================================================================

def get_job_skills(job_id):
    """Lấy danh sách skills theo job_id từ mapping"""
    for mapping in mapping_database['job_skill_mappings']:
        if mapping['job_id'] == job_id:
            required_skills = set()
            # Thêm required skills
            for skill_id in mapping.get('required_skills', []):
                if skill_id in SKILL_ID_TO_NAME:
                    required_skills.add(SKILL_ID_TO_NAME[skill_id])
            
            # Xử lý alternatives - chỉ cần 1 trong số các skills trong nhóm
            alternatives = mapping.get('skill_alternatives', [])
            
            return {
                'required': required_skills,
                'alternatives': alternatives,
                'preferred': [SKILL_ID_TO_NAME[sid] for sid in mapping.get('preferred_skills', []) if sid in SKILL_ID_TO_NAME]
            }
    return {'required': set(), 'alternatives': [], 'preferred': []}

def check_alternatives_satisfied(student_skills, alternatives):
    """Kiểm tra xem student có ít nhất 1 skill trong mỗi nhóm alternatives không
    
    Returns:
        satisfied: List of dicts with alt_group info and matched_skills
        missing: List of alt_groups that student doesn't have any skill from
    """
    satisfied = []
    missing = []
    
    for alt_group in alternatives:
        skills_in_group = [SKILL_ID_TO_NAME[sid] for sid in alt_group['one_of'] if sid in SKILL_ID_TO_NAME]
        # Tìm các skill mà student có trong nhóm này
        matched_skills = [skill for skill in skills_in_group if skill in student_skills]
        
        if matched_skills:
            # Lưu cả alt_group và các skill cụ thể mà student có
            satisfied.append({
                'alt_group': alt_group,
                'matched_skills': matched_skills
            })
        else:
            missing.append(alt_group)
    
    return satisfied, missing

def goi_y_nganh_nghe(ky_nang_sinh_vien):
    """Gợi ý các ngành nghề phù hợp dựa trên kỹ năng của sinh viên"""
    sk_sv = set(ky_nang_sinh_vien)
    goi_y = {}
    
    # Duyệt qua tất cả jobs
    for job_id, job_info in JOB_ID_TO_INFO.items():
        job_skills = get_job_skills(job_id)
        required = job_skills['required']
        alternatives = job_skills['alternatives']
        
        # Tính số skills required mà student có
        matched_required = sk_sv & required
        
        # Kiểm tra alternatives
        satisfied_alts, missing_alts = check_alternatives_satisfied(sk_sv, alternatives)
        
        # Tính tổng skills cần thiết (required + số nhóm alternatives)
        total_needed = len(required) + len(alternatives)
        
        if total_needed == 0:
            continue
            
        # Lấy danh sách skills khớp từ alternatives
        matched_alt_skills = []
        for alt_info in satisfied_alts:
            matched_alt_skills.extend(alt_info['matched_skills'])
        
        # Tính số skills đã thỏa mãn
        total_matched = len(matched_required) + len(satisfied_alts)
        total_missing = len(required - sk_sv) + len(missing_alts)
        
        # CHỈ thêm vào gợi ý nếu có ít nhất 1 kỹ năng khớp
        if total_matched == 0:
            continue
        
        nganh_name = job_info['title_vi']
        goi_y[nganh_name] = {
            "ky_nang_khop": list(matched_required) + matched_alt_skills,
            "ky_nang_con_thieu": list(required - sk_sv) + [alt['note'] for alt in missing_alts],
            "so_ky_nang_thieu": total_missing
        }
    
    # Sắp xếp theo số kỹ năng thiếu tăng dần (ít thiếu nhất = phù hợp nhất)
    goi_y_da_sap_xep = dict(sorted(goi_y.items(), key=lambda item: item[1]['so_ky_nang_thieu']))
    
    # TODO: Xử lý trường hợp user có kỹ năng nhưng không có ngành nào phù hợp
    # if not goi_y_da_sap_xep and ky_nang_sinh_vien:
    #     return {"thong_bao": "Bạn đã có kỹ năng nhưng chưa có ngành nào phù hợp trong hệ thống"}
    
    return goi_y_da_sap_xep

def kiem_tra_khoang_cach_ky_nang(chon_nganh, ky_nang_sinh_vien):
    """Kiểm tra khoảng cách kỹ năng giữa sinh viên và ngành nghề đã chọn"""
    sk_sv = set(ky_nang_sinh_vien)
    
    if chon_nganh not in JOB_TITLE_TO_ID:
        return {"loi": f"Không tìm thấy ngành '{chon_nganh}'."}
    
    job_id = JOB_TITLE_TO_ID[chon_nganh]
    job_skills = get_job_skills(job_id)
    
    required = job_skills['required']
    alternatives = job_skills['alternatives']
    preferred = set(job_skills['preferred'])
    
    # Skills đã có (required)
    ky_nang_da_co = sk_sv & required
    
    # Skills còn thiếu (required)
    ky_nang_thieu = required - sk_sv
    
    # Kiểm tra alternatives
    satisfied_alts, missing_alts = check_alternatives_satisfied(sk_sv, alternatives)
    
    # Tạo danh sách kỹ năng yêu cầu (bao gồm alternatives)
    ky_nang_yeu_cau = list(required)
    for alt in alternatives:
        ky_nang_yeu_cau.append(alt['note'])
    
    # Lấy matched skills từ alternatives
    matched_alt_skills = []
    for alt_info in satisfied_alts:
        matched_alt_skills.extend(alt_info['matched_skills'])
    
    # Thêm alternatives vào danh sách đã có/thiếu
    ky_nang_da_co_full = list(ky_nang_da_co) + matched_alt_skills
    ky_nang_thieu_full = list(ky_nang_thieu)
    
    # Xử lý missing alternatives - thêm chi tiết các lựa chọn
    missing_alts_details = []
    for alt in missing_alts:
        # Lấy danh sách skill names từ skill IDs trong 'one_of'
        skill_names = [SKILL_ID_TO_NAME[sid] for sid in alt['one_of'] if sid in SKILL_ID_TO_NAME]
        # Tạo string với các lựa chọn skill
        options = " HOẶC ".join(skill_names)
        missing_alts_details.append(f"{alt['note']}: ({options})")
    
    # Preferred skills (không bắt buộc)
    preferred_co = sk_sv & preferred
    preferred_thieu = preferred - sk_sv
    
    return {
        "nganh_da_chon": chon_nganh,
        "ky_nang_yeu_cau": ky_nang_yeu_cau,
        "ky_nang_da_co": ky_nang_da_co_full,
        "ky_nang_can_hoc_them": ky_nang_thieu_full,
        "ky_nang_can_hoc_them_chi_tiet": missing_alts_details,  # Thêm chi tiết alternatives
        "ky_nang_nen_co": list(preferred_co),
        "ky_nang_nen_hoc": list(preferred_thieu)
    }

# ===================================================================
# PHẦN 3: GIAO DIỆN NGƯỜI DÙNG (GUI) VỚI CUSTOMTKINTER
# ===================================================================

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class CareerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Ứng dụng Tư vấn Hướng nghiệp (Đã sửa lỗi)")
        self.geometry("750x600")

        self.tabControl = ctk.CTkTabview(self, width=700, height=550)
        self.tabControl.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab1 = self.tabControl.add('1. Tìm Ngành theo Kỹ năng')
        self.tab2 = self.tabControl.add('2. Tìm Kỹ năng theo Ngành')

        self.skill_widgets_tab1 = {}
        self.skill_widgets_tab2 = {}

        # *** THAY ĐỔI: Tạo biến StringVar để theo dõi ô tìm kiếm ***
        self.skill_search_var1 = ctk.StringVar()
        self.skill_search_var2 = ctk.StringVar()
        
        # *** THÊM: StringVar cho ComboBox ngành nghề ***
        self.career_search_var = ctk.StringVar()
        self.filtered_careers = ALL_CAREERS.copy()

        self.create_tab1_widgets()
        self.create_tab2_widgets()

    def create_skill_checkboxes(self, parent_frame, skill_widgets_dict):
        scrollable_frame = ctk.CTkScrollableFrame(parent_frame, width=200, height=300)
        for skill in ALL_SKILLS:
            var = ctk.IntVar() 
            cb = ctk.CTkCheckBox(scrollable_frame, text=skill, variable=var)
            cb.pack(anchor='w', padx=10, pady=5)
            skill_widgets_dict[skill] = {"var": var, "widget": cb}
        return scrollable_frame
            
    def get_selected_skills(self, skill_widgets_dict):
        return [skill for skill, data in skill_widgets_dict.items() if data["var"].get() == 1]

    # --- Hàm lọc (Không đổi) ---
    def _filter_skills(self, query, skill_widgets_dict):
        query = query.lower()
        for skill, data in skill_widgets_dict.items():
            widget = data["widget"]
            if query in skill.lower():
                widget.pack(anchor='w', padx=10, pady=5)
            else:
                widget.pack_forget()

    # --- HÀM LỌC ĐÃ SỬA ---
    # Hàm lọc riêng cho Tab 1
    def filter_skills_tab1(self, *args): # Chấp nhận các tham số rác từ trace
        query = self.skill_search_var1.get() # Lấy query từ StringVar
        self._filter_skills(query, self.skill_widgets_tab1)

    # Hàm lọc riêng cho Tab 2
    def filter_skills_tab2(self, *args): # Chấp nhận các tham số rác từ trace
        query = self.skill_search_var2.get() # Lấy query từ StringVar
        self._filter_skills(query, self.skill_widgets_tab2)
    
    # --- HÀM LỌC NGÀNH NGHỀ (AUTOCOMPLETE) ---
    def filter_careers(self, *args):
        query = self.career_search_var.get().lower()
        
        # Xóa listbox hiện tại
        self.career_listbox.delete(0, END)
        
        if query:
            # Lọc các ngành phù hợp
            self.filtered_careers = [career for career in ALL_CAREERS if query in career.lower()]
        else:
            # Hiển thị tất cả nếu không có query
            self.filtered_careers = ALL_CAREERS.copy()
        
        # Thêm vào listbox
        for career in self.filtered_careers:
            self.career_listbox.insert(END, career)
        
        # Hiển thị listbox nếu có kết quả
        if self.filtered_careers:
            self.career_listbox.pack(fill="x", padx=10, pady=(2, 5))
            # Tự động chọn item đầu tiên
            if self.career_listbox.size() > 0:
                self.career_listbox.selection_clear(0, END)
                self.career_listbox.selection_set(0)
                self.career_listbox.activate(0)
        else:
            self.career_listbox.pack_forget()
    
    def on_career_select(self, event):
        """Khi chọn ngành từ listbox bằng click"""
        if self.career_listbox.curselection():
            index = self.career_listbox.curselection()[0]
            selected_career = self.career_listbox.get(index)
            self.career_search_var.set(selected_career)
            self.career_listbox.pack_forget()  # Ẩn listbox sau khi chọn
            self.career_entry.focus_set()  # Trả focus về entry
    
    def on_career_entry_keypress(self, event):
        """Xử lý phím Enter và mũi tên trong Entry"""
        if event.keysym == 'Return':  # Enter
            # Chọn item đang được highlight trong listbox
            if self.career_listbox.winfo_ismapped() and self.career_listbox.curselection():
                index = self.career_listbox.curselection()[0]
                selected_career = self.career_listbox.get(index)
                self.career_search_var.set(selected_career)
                self.career_listbox.pack_forget()
            return "break"
        
        elif event.keysym == 'Down':  # Mũi tên xuống
            if self.career_listbox.winfo_ismapped():
                current = self.career_listbox.curselection()
                if current:
                    next_index = min(current[0] + 1, self.career_listbox.size() - 1)
                else:
                    next_index = 0
                self.career_listbox.selection_clear(0, END)
                self.career_listbox.selection_set(next_index)
                self.career_listbox.activate(next_index)
                self.career_listbox.see(next_index)
            else:
                # Hiển thị listbox nếu đang ẩn
                self.filter_careers()
            return "break"
        
        elif event.keysym == 'Up':  # Mũi tên lên
            if self.career_listbox.winfo_ismapped():
                current = self.career_listbox.curselection()
                if current:
                    prev_index = max(current[0] - 1, 0)
                else:
                    prev_index = 0
                self.career_listbox.selection_clear(0, END)
                self.career_listbox.selection_set(prev_index)
                self.career_listbox.activate(prev_index)
                self.career_listbox.see(prev_index)
            return "break"
        
        elif event.keysym == 'Escape':  # ESC để đóng
            self.career_listbox.pack_forget()
            return "break"
    
    def on_career_entry_focus_in(self, event):
        """Khi focus vào ô nhập ngành, hiển thị tất cả ngành"""
        self.filter_careers()
    
    def on_career_entry_focus_out(self, event):
        """Khi mất focus, ẩn listbox sau một chút để cho phép click vào listbox"""
        self.after(200, lambda: self.career_listbox.pack_forget())

    # --- Tab 1: ĐÃ SỬA ---
    def create_tab1_widgets(self):
        self.tab1.grid_columnconfigure(0, weight=1)
        self.tab1.grid_columnconfigure(1, weight=2)
        self.tab1.grid_rowconfigure(0, weight=1)

        skills_frame = ctk.CTkFrame(self.tab1, fg_color="transparent")
        skills_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        skills_label = ctk.CTkLabel(skills_frame, text="Chọn các kỹ năng bạn đã có", font=ctk.CTkFont(weight="bold"))
        skills_label.pack(pady=(0, 5))
        
        # *** THAY ĐỔI: Gán textvariable cho ô tìm kiếm ***
        self.skill_search_tab1 = ctk.CTkEntry(skills_frame, 
                                              placeholder_text="Tìm kiếm kỹ năng...",
                                              textvariable=self.skill_search_var1) # Gán var
        self.skill_search_tab1.pack(fill="x", padx=10, pady=(0, 5))
        
        # *** THAY ĐỔI: Dùng trace thay cho bind ***
        self.skill_search_var1.trace_add("write", self.filter_skills_tab1)

        scroll_frame = self.create_skill_checkboxes(skills_frame, self.skill_widgets_tab1)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        right_frame = ctk.CTkFrame(self.tab1, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        btn_find_career = ctk.CTkButton(right_frame, text="Tìm ngành phù hợp", command=self.on_find_career)
        btn_find_career.pack(pady=10)
        
        self.result_text_tab1 = ctk.CTkTextbox(right_frame, height=20, width=50)
        self.result_text_tab1.pack(fill="both", expand=True)

    def on_find_career(self):
        # (Không thay đổi)
        selected_skills = self.get_selected_skills(self.skill_widgets_tab1)
        if not selected_skills:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn ít nhất một kỹ năng.")
            return
        results = goi_y_nganh_nghe(selected_skills)
        self.result_text_tab1.delete("1.0", "end")
        
        # Kiểm tra nếu không có ngành nào phù hợp
        if not results:
            self.result_text_tab1.insert("end", "⚠️ KHÔNG TÌM THẤY NGÀNH PHÙ HỢP\n\n")
            self.result_text_tab1.insert("end", f"Bạn đã chọn {len(selected_skills)} kỹ năng:\n")
            self.result_text_tab1.insert("end", f"{', '.join(selected_skills)}\n\n")
            self.result_text_tab1.insert("end", "Nhưng không có ngành nghề nào trong hệ thống yêu cầu các kỹ năng này.\n")
            self.result_text_tab1.insert("end", "💡 Gợi ý: Thử chọn thêm các kỹ năng khác hoặc kiểm tra lại danh sách kỹ năng.")
            return
        
        self.result_text_tab1.insert("end", "--- Gợi ý ngành nghề (xếp theo mức độ phù hợp) ---\n\n")
        for nganh, info in results.items():
            self.result_text_tab1.insert("end", f"NGÀNH: {nganh}\n")
            self.result_text_tab1.insert("end", f" - Số kỹ năng còn thiếu: {info['so_ky_nang_thieu']}\n")
            self.result_text_tab1.insert("end", f" - Kỹ năng đã khớp: {', '.join(info['ky_nang_khop']) or 'Không có'}\n")
            self.result_text_tab1.insert("end", f" - Kỹ năng cần học thêm: {', '.join(info['ky_nang_con_thieu']) or 'Không có'}\n")
            self.result_text_tab1.insert("end", "-"*30 + "\n")

    # --- Tab 2: ĐÃ SỬA ---
    def create_tab2_widgets(self):
        self.tab2.grid_columnconfigure(0, weight=1)
        self.tab2.grid_columnconfigure(1, weight=2)
        self.tab2.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.tab2, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 1. Chọn ngành (AUTOCOMPLETE DROPDOWN)
        career_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        career_frame.pack(fill="x", pady=10)
        career_label = ctk.CTkLabel(career_frame, text="1. Chọn một ngành (↑↓ điều hướng, Enter chọn)", font=ctk.CTkFont(weight="bold", size=13))
        career_label.pack(anchor="w", padx=10)
        
        # *** Entry để nhập và tìm kiếm ***
        self.career_entry = ctk.CTkEntry(
            career_frame,
            placeholder_text="💼 Nhập tên ngành hoặc click để xem danh sách...",
            textvariable=self.career_search_var,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.career_entry.pack(fill="x", padx=10, pady=(5, 0))
        self.career_entry.bind("<FocusIn>", self.on_career_entry_focus_in)
        self.career_entry.bind("<FocusOut>", self.on_career_entry_focus_out)
        self.career_entry.bind("<KeyPress>", self.on_career_entry_keypress)
        
        # *** Listbox để hiển thị gợi ý (ban đầu ẩn) ***
        self.career_listbox = Listbox(
            career_frame,
            height=7,
            font=("Segoe UI", 11),
            bg="#2b2b2b",
            fg="#E0E0E0",
            selectbackground="#1f6aa5",
            selectforeground="white",
            activestyle="none",
            borderwidth=2,
            relief="solid",
            highlightthickness=0,
            bd=0
        )
        self.career_listbox.bind("<Button-1>", self.on_career_select)
        # Ban đầu không pack (ẩn)
        
        # Đặt giá trị mặc định
        self.career_search_var.set(ALL_CAREERS[0])
        
        # *** Theo dõi thay đổi để lọc ***
        self.career_search_var.trace_add("write", self.filter_careers)

        # 2. Chọn kỹ năng
        skills_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        skills_frame.pack(fill="both", expand=True, pady=10)
        skills_label = ctk.CTkLabel(skills_frame, text="2. Chọn kỹ năng bạn đã có", font=ctk.CTkFont(weight="bold"))
        skills_label.pack(anchor="w", padx=10, pady=(0, 5))

        # *** THAY ĐỔI: Gán textvariable cho ô tìm kiếm ***
        self.skill_search_tab2 = ctk.CTkEntry(skills_frame, 
                                              placeholder_text="Tìm kiếm kỹ năng...",
                                              textvariable=self.skill_search_var2) # Gán var
        self.skill_search_tab2.pack(fill="x", padx=10, pady=(0, 5))
        
        # *** THAY ĐỔI: Dùng trace thay cho bind ***
        self.skill_search_var2.trace_add("write", self.filter_skills_tab2)

        scroll_frame = self.create_skill_checkboxes(skills_frame, self.skill_widgets_tab2)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # (Phần còn lại không thay đổi)
        right_frame = ctk.CTkFrame(self.tab2, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        btn_check_skills = ctk.CTkButton(right_frame, text="Kiểm tra kỹ năng", command=self.on_check_skills)
        btn_check_skills.pack(pady=10)
        
        self.result_text_tab2 = ctk.CTkTextbox(right_frame, height=20, width=50)
        self.result_text_tab2.pack(fill="both", expand=True)

    def on_check_skills(self):
        # Lấy ngành từ Entry (đã thay đổi từ ComboBox)
        career = self.career_search_var.get().strip()
        
        # Kiểm tra xem có nhập ngành không
        if not career:
            messagebox.showwarning("Chưa chọn ngành", "Vui lòng chọn một ngành nghề.")
            return
        
        selected_skills = self.get_selected_skills(self.skill_widgets_tab2)
        
        results = kiem_tra_khoang_cach_ky_nang(career, selected_skills)
        
        self.result_text_tab2.delete("1.0", "end")
        
        if "loi" in results:
            self.result_text_tab2.insert("end", f"LỖI: {results['loi']}\n")
            self.result_text_tab2.insert("end", "Vui lòng chọn một ngành có trong danh sách.")
            return

        self.result_text_tab2.insert("end", f"--- Phân tích cho ngành: {results['nganh_da_chon']} ---\n\n")
        self.result_text_tab2.insert("end", f"✅ KỸ NĂNG YÊU CẦU ({len(results['ky_nang_yeu_cau'])}):\n")
        self.result_text_tab2.insert("end", f"{', '.join(results['ky_nang_yeu_cau'])}\n\n")
        
        self.result_text_tab2.insert("end", f"✔️ Kỹ năng bạn đã có ({len(results['ky_nang_da_co'])}):\n")
        self.result_text_tab2.insert("end", f"{', '.join(results['ky_nang_da_co']) or 'Chưa có'}\n\n")
        
        # Hiển thị kỹ năng cần học thêm
        total_missing = len(results['ky_nang_can_hoc_them']) + len(results.get('ky_nang_can_hoc_them_chi_tiet', []))
        self.result_text_tab2.insert("end", f"❌ KỸ NĂNG CẦN HỌC THÊM ({total_missing}):\n")
        
        # Hiển thị required skills còn thiếu
        if results['ky_nang_can_hoc_them']:
            self.result_text_tab2.insert("end", f"{', '.join(results['ky_nang_can_hoc_them'])}\n")
        
        # Hiển thị alternatives còn thiếu với các lựa chọn chi tiết
        if results.get('ky_nang_can_hoc_them_chi_tiet'):
            if results['ky_nang_can_hoc_them']:
                self.result_text_tab2.insert("end", "\n")
            for alt_detail in results['ky_nang_can_hoc_them_chi_tiet']:
                self.result_text_tab2.insert("end", f"• {alt_detail}\n")
        
        if not results['ky_nang_can_hoc_them'] and not results.get('ky_nang_can_hoc_them_chi_tiet'):
            self.result_text_tab2.insert("end", "Đã đủ kỹ năng bắt buộc!")
        
        self.result_text_tab2.insert("end", "\n")
        
        # Hiển thị preferred skills nếu có
        if results.get('ky_nang_nen_co') or results.get('ky_nang_nen_hoc'):
            self.result_text_tab2.insert("end", "--- KỸ NĂNG NÊN CÓ (không bắt buộc) ---\n\n")
            
            if results['ky_nang_nen_co']:
                self.result_text_tab2.insert("end", f"⭐ Kỹ năng nên có bạn đã có ({len(results['ky_nang_nen_co'])}):\n")
                self.result_text_tab2.insert("end", f"{', '.join(results['ky_nang_nen_co'])}\n\n")
            
            if results['ky_nang_nen_hoc']:
                self.result_text_tab2.insert("end", f"💡 Kỹ năng nên học thêm ({len(results['ky_nang_nen_hoc'])}):\n")
                self.result_text_tab2.insert("end", f"{', '.join(results['ky_nang_nen_hoc'])}\n")

# ===================================================================
# PHẦN 3: CHẠY ỨNG DỤNG
# ===================================================================

if __name__ == "__main__":
    app = CareerApp()
    app.mainloop()