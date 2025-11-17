"""
Custom Selection Listbox Widget - Thay thế cho hàng ngàn checkboxes
Hiệu suất cao, hỗ trợ multi-select và search
"""
import customtkinter as ctk
from typing import List, Tuple, Set


class SelectionListbox(ctk.CTkFrame):
    """Custom listbox widget với multi-select, search, và virtual scrolling"""
    
    def __init__(self, master, items: List[Tuple[str, str]], **kwargs):
        """
        Args:
            master: Parent widget
            items: List of (display_name, canonical_name) tuples
        """
        super().__init__(master, **kwargs)
        
        # Data
        self.all_items = items  # [(display, canonical), ...]
        self.filtered_items = items.copy()
        self.selected_items: Set[str] = set()  # Set of display names
        self.canonical_map = {display: canonical for display, canonical in items}
        
        # Search box
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text="🔍 Search...",
            height=30
        )
        self.search_entry.pack(fill="x", padx=5, pady=(5, 0))
        self.search_var.trace_add("write", lambda *args: self._on_search())
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Select All",
            command=self.select_all,
            width=80,
            height=25,
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Clear All",
            command=self.clear_all,
            width=80,
            height=25,
            font=ctk.CTkFont(size=10)
        ).pack(side="left", padx=2)
        
        # Listbox container với scrollbar
        self.listbox_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray20")
        )
        self.listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Item buttons (tạo khi cần)
        self.item_buttons = {}
        
        # Initial render
        self._render_items()
    
    def _render_items(self):
        """Render các items hiện tại"""
        # Clear old buttons
        for btn in self.item_buttons.values():
            btn.destroy()
        self.item_buttons.clear()
        
        # Render filtered items (giới hạn 500 items để tránh lag)
        display_items = self.filtered_items[:140]
        
        for display_name, canonical_name in display_items:
            is_selected = display_name in self.selected_items
            
            btn = ctk.CTkButton(
                self.listbox_frame,
                text=f"{'✓' if is_selected else '○'} {display_name}",
                command=lambda d=display_name: self._toggle_item(d),
                anchor="w",
                fg_color=("gray85", "gray30") if is_selected else ("gray90", "gray25"),
                hover_color=("gray80", "gray35"),
                font=ctk.CTkFont(size=11),
                height=28
            )
            btn.pack(fill="x", pady=1, padx=2)
            self.item_buttons[display_name] = btn
        
        # Hiển thị thông báo nếu bị giới hạn
        # if len(self.filtered_items) > 500:
        #     info_label = ctk.CTkLabel(
        #         self.listbox_frame,
        #         text=f"⚠️ Showing first 500 of {len(self.filtered_items)} items. Use search to filter.",
        #         font=ctk.CTkFont(size=10),
        #         text_color="orange"
        #     )
        #     info_label.pack(pady=5)
    
    def _toggle_item(self, display_name: str):
        """Toggle selection của một item"""
        if display_name in self.selected_items:
            self.selected_items.remove(display_name)
        else:
            self.selected_items.add(display_name)
        
        # Update button
        if display_name in self.item_buttons:
            btn = self.item_buttons[display_name]
            is_selected = display_name in self.selected_items
            btn.configure(
                text=f"{'✓' if is_selected else '○'} {display_name}",
                fg_color=("gray85", "gray30") if is_selected else ("gray90", "gray25")
            )
    
    def _on_search(self):
        """Handle search"""
        query = self.search_var.get().lower().strip()
        
        if not query:
            self.filtered_items = self.all_items.copy()
        else:
            self.filtered_items = [
                (display, canonical)
                for display, canonical in self.all_items
                if query in display.lower()
            ]
        
        self._render_items()
    
    def select_all(self):
        """Select tất cả filtered items"""
        for display_name, _ in self.filtered_items[:500]:  # Chỉ select items đang hiển thị
            self.selected_items.add(display_name)
        self._render_items()
    
    def clear_all(self):
        """Clear tất cả selections"""
        self.selected_items.clear()
        self._render_items()
    
    def get_selected_canonical(self) -> List[str]:
        """Lấy danh sách canonical names đã chọn"""
        return list(set([
            self.canonical_map[display]
            for display in self.selected_items
            if display in self.canonical_map
        ]))
    
    def get_selected_display(self) -> List[str]:
        """Lấy danh sách display names đã chọn"""
        return list(self.selected_items)
