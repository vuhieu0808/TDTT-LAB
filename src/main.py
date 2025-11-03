import customtkinter as ctk
from tkinter import messagebox, Listbox, END
import json

# ===================================================================
# PHẦN 1: LOGIC CỐT LÕI (Giữ nguyên)
# ===================================================================

CAREER_SKILLS_DB = {
    "Kỹ thuật phần mềm": {"Python", "Git", "Cấu trúc dữ liệu", "Giải thuật", "SQL"},
    "Khoa học dữ liệu": {"Python", "SQL", "Thống kê", "Học máy", "Pandas"},
    "Lập trình Web (Frontend)": {"HTML", "CSS", "JavaScript", "React", "Git"},
    "Kỹ sư DevOps": {"Linux", "Docker", "Kubernetes", "Git", "Python", "CI/CD"},
    "Thiết kế UX/UI": {"Figma", "Adobe XD", "User Research", "Prototyping"},
    "Quản trị Mạng": {"Cisco", "Linux", "Security", "Networking Concepts"},
    "Lập trình Game": {"C++", "Unity", "Unreal Engine", "Toán học 3D"},
    "An toàn Thông tin": {"Linux", "Security", "Penetration Testing", "Cryptography"}
}

ALL_SKILLS = sorted(list(set.union(*CAREER_SKILLS_DB.values())))
ALL_CAREERS = sorted(list(CAREER_SKILLS_DB.keys()))

def goi_y_nganh_nghe(ky_nang_sinh_vien):
    sk_sv = set(ky_nang_sinh_vien)
    goi_y = {}
    for nganh, ky_nang_yeu_cau in CAREER_SKILLS_DB.items():
        ky_nang_thieu = ky_nang_yeu_cau - sk_sv
        ky_nang_khop = ky_nang_yeu_cau.intersection(sk_sv)
        goi_y[nganh] = {
            "ky_nang_khop": list(ky_nang_khop),
            "ky_nang_con_thieu": list(ky_nang_thieu),
            "so_ky_nang_thieu": len(ky_nang_thieu)
        }
    goi_y_da_sap_xep = dict(sorted(goi_y.items(), key=lambda item: item[1]['so_ky_nang_thieu']))
    return goi_y_da_sap_xep

def kiem_tra_khoang_cach_ky_nang(chon_nganh, ky_nang_sinh_vien):
    sk_sv = set(ky_nang_sinh_vien)
    if chon_nganh not in CAREER_SKILLS_DB:
        return {"loi": f"Không tìm thấy ngành '{chon_nganh}'."}
    ky_nang_yeu_cau = CAREER_SKILLS_DB[chon_nganh]
    ky_nang_thieu = ky_nang_yeu_cau - sk_sv
    ky_nang_da_co = ky_nang_yeu_cau.intersection(sk_sv)
    return {
        "nganh_da_chon": chon_nganh,
        "ky_nang_yeu_cau": list(ky_nang_yeu_cau),
        "ky_nang_da_co": list(ky_nang_da_co),
        "ky_nang_can_hoc_them": list(ky_nang_thieu)
    }

# ===================================================================
# PHẦN 2: GIAO DIỆN NGƯỜI DÙNG (GUI) VỚI CUSTOMTKINTER
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
        self.result_text_tab2.insert("end", f"Kỹ năng yêu cầu ({len(results['ky_nang_yeu_cau'])}):\n{', '.join(results['ky_nang_yeu_cau'])}\n\n")
        self.result_text_tab2.insert("end", f"Kỹ năng bạn đã có ({len(results['ky_nang_da_co'])}):\n{', '.join(results['ky_nang_da_co']) or 'Không có'}\n\n")
        self.result_text_tab2.insert("end", f"KỸ NĂNG CẦN HỌC THÊM ({len(results['ky_nang_can_hoc_them'])}):\n{', '.join(results['ky_nang_can_hoc_them']) or 'Đã đủ kỹ năng!'}\n")

# ===================================================================
# PHẦN 3: CHẠY ỨNG DỤNG
# ===================================================================

if __name__ == "__main__":
    app = CareerApp()
    app.mainloop()