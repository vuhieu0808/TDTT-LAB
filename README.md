# 🎓 Student Career Helper

Ứng dụng giúp sinh viên mới ra trường giải quyết vấn đề thất nghiệp bằng cách:

- Tìm công việc phù hợp với kỹ năng hiện có
- Tạo roadmap học tập để đạt được công việc mục tiêu
- Đề xuất project thực hành để củng cố kiến thức

## ✨ Tính năng

### Tab 1: Tìm Job Phù Hợp

- Nhập skills và knowledge bạn đang có
- Hệ thống sẽ tìm và xếp hạng các công việc phù hợp
- Hiển thị điểm số, kỹ năng còn thiếu, và kỹ năng đã có

### Tab 2: Tạo Roadmap Học Tập

- Nhập công việc mục tiêu
- Nhập skills và knowledge hiện tại
- Hệ thống tạo roadmap học tập tối ưu:
  - Sử dụng **Topological Sort** để sắp xếp thứ tự học
  - Phát hiện **chu trình** và đề xuất học song song
  - Sắp xếp theo **độ khó** (level)
  - Ước tính thời gian học
- Đề xuất project thực hành sử dụng **Google Gemini AI**

## 📋 Yêu cầu

- Python 3.8 trở lên
- CustomTkinter
- Google Gemini API (optional, để đề xuất project)

## 🚀 Cài đặt

1. **Clone hoặc download project**

2. **Cài đặt dependencies:**

```bash
pip install -r requirements.txt
```

3. **Chuẩn bị dữ liệu:**

   - Đảm bảo có các file trong thư mục `src/`:
     - `data.json` - Thông tin các công việc
     - `skill.json` - Danh sách tất cả skills
     - `knowledge.json` - Danh sách tất cả knowledge
     - `knowledge.txt` - Thông tin chi tiết về độ khó, prerequisites của mỗi skill/knowledge

4. **Lấy Google Gemini API Key (optional):**
   - Truy cập: https://makersuite.google.com/app/apikey
   - Tạo API key mới
   - Copy API key

## 💻 Chạy ứng dụng

### Cách 1: Chạy trực tiếp

```bash
cd src
python main_app.py
```

### Cách 2: Set environment variable cho API key

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY = "your-api-key-here"
python main_app.py

# Windows CMD
set GOOGLE_API_KEY=your-api-key-here
python main_app.py

# Linux/Mac
export GOOGLE_API_KEY=your-api-key-here
python main_app.py
```

## 📖 Hướng dẫn sử dụng

### Tab 1: Tìm Job Phù Hợp

1. Nhập skills vào ô bên trái (mỗi dòng một skill)

   ```
   JavaScript
   Python (computer programming)
   DevOps
   ```

2. Nhập knowledge vào ô bên phải (mỗi dòng một knowledge)

   ```
   cloud technologies
   database
   web programming
   ```

3. Click **"🔍 Tìm Jobs Phù Hợp"**

4. Xem kết quả:
   - Danh sách jobs được xếp hạng theo điểm phù hợp
   - Skills/knowledge còn thiếu
   - Skills/knowledge đã có

### Tab 2: Tạo Roadmap Học Tập

1. Nhập tên công việc mục tiêu:

   ```
   cloud DevOps engineer
   ```

2. Nhập skills và knowledge hiện có (tương tự Tab 1)

3. **(Optional)** Nhập Google Gemini API Key nếu muốn đề xuất project

4. Click **"🗺️ Tạo Roadmap"**

   - Xem roadmap học tập chi tiết
   - Các giai đoạn học (stages)
   - Items có thể học song song
   - Độ khó và thời gian ước tính

5. Click **"💡 Đề Xuất Project"** sau khi có roadmap
   - Hệ thống sẽ dùng Gemini AI để tạo project thực hành
   - Nếu không có API key, sẽ dùng project mẫu

## 🏗️ Cấu trúc Project

```
src/
├── main_app.py              # GUI chính với CustomTkinter
├── data_loader.py           # Load và quản lý dữ liệu
├── job_matcher.py           # Matching jobs với user profile
├── graph_utils.py           # Topological sort và xử lý đồ thị
├── roadmap_generator.py     # Tạo roadmap học tập
├── ai_project_suggester.py  # Tích hợp Google Gemini AI
├── requirements.txt         # Dependencies
├── data.json               # Database công việc
├── skill.json              # Database skills
├── knowledge.json          # Database knowledge
└── knowledge.txt               # Chi tiết về skills (level, prerequisites)
```

## 🔧 Công nghệ sử dụng

- **CustomTkinter**: Modern GUI framework cho Python
- **Topological Sort**: Sắp xếp thứ tự học hợp lý
- **Cycle Detection**: Phát hiện chu trình để học song song
- **Google Gemini AI**: Đề xuất project thực hành thông minh

## 🎯 Thuật toán Topological Sort

Ứng dụng sử dụng thuật toán Topological Sort để:

1. Xây dựng đồ thị dependencies giữa các skills/knowledge
2. Phát hiện chu trình (cyclic dependencies)
3. Sắp xếp thứ tự học từ dễ đến khó
4. Nhóm các items có thể học song song

### Xử lý chu trình

- Nếu có chu trình (A cần B, B cần A), các items trong chu trình được đánh dấu "có thể học song song"
- Sắp xếp theo độ khó (level) trong cùng một nhóm

## 📝 Ví dụ

### Input Tab 1:

**Skills:**

```
JavaScript
Python (computer programming)
```

**Knowledge:**

```
cloud technologies
database
```

**Output:** Top 10 jobs phù hợp với điểm số và phân tích chi tiết

### Input Tab 2:

**Job:** `cloud DevOps engineer`  
**Skills:** `JavaScript`  
**Knowledge:** `cloud technologies`

**Output:**

- Roadmap với 5 giai đoạn
- 15 items cần học
- Thời gian ước tính: 3.2 tháng
- Project đề xuất: "Cloud Infrastructure Automation System"

## ⚠️ Lưu ý

- Dữ liệu trong `data.json`, `skill.json`, `knowledge.json`, `knowledge.txt` phải được chuẩn bị sẵn
- Google Gemini API có thể có giới hạn rate limit
- Nếu không có API key, ứng dụng vẫn hoạt động với project mẫu

## 🐛 Troubleshooting

### Lỗi: "Import could not be resolved"

```bash
pip install customtkinter google-generativeai
```

### Lỗi: "Không tìm thấy file data.json"

- Đảm bảo bạn chạy `python main_app.py` từ trong thư mục `src/`
- Hoặc cập nhật `data_dir` trong `DataLoader`

### Lỗi Gemini API

- Kiểm tra API key có đúng không
- Kiểm tra kết nối internet
- Xem quota API tại Google AI Studio

## 📄 License

Educational project - Free to use and modify

## 👨‍💻 Author

Sinh viên TDTT - Midterm Project

---

**Happy Learning! 🚀📚**
