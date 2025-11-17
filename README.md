[en](README-en.md) | vi

# 🎓 Student Career Helper

## Tổng quan
Ứng dụng giúp sinh viên mới ra trường giải quyết vấn đề thất nghiệp bằng cách:

- Tìm công việc phù hợp với kỹ năng hiện có
- Tạo roadmap học tập để đạt được công việc mục tiêu
- Đề xuất project thực hành để củng cố kiến thức

## ✨ Tính năng

### Tìm Job Phù Hợp

- Nhập skills và knowledge bạn đang có
- Hệ thống sẽ tìm và xếp hạng các công việc phù hợp
- Hiển thị điểm số, kỹ năng còn thiếu, và kỹ năng đã có

### Tạo Roadmap Học Tập

- Nhập công việc mục tiêu
- Nhập skills và knowledge hiện tại
- Hệ thống tạo roadmap học tập tối ưu:
  - Sử dụng **Topological Sort** để sắp xếp thứ tự học
  - Phát hiện **chu trình** và đề xuất học song song
  - Sắp xếp theo **độ khó** (level)
  - Ước tính thời gian học
- Đề xuất project thực hành sử dụng **Google Gemini AI**

## Yêu cầu:
- Python 3.8 hoặc mới hơn
- Dart SDK 3.9 hoặc mới hơn

## 🚀 Cài đặt & chạy
### 0. Setup
- Tại thư mục gốc, tạo file `.env` với API key (vd như trong [.env.example](.env.example))
```
GOOGLE_API_KEY=AIzaSy....
```

- Đảm bảo Python đã được cài đặt và đã kích hoạt môi trường ảo Python

- Cài đặt dependencies cho Python
```
pip install -r requirements.txt
```

### 0.5. Về dữ liệu có sẵn
- Mặc định project dùng dữ liệu đã được biên soạn sẵn trong thư mục [assets](assets). Nếu muốn tái tạo dữ liệu, đi đến bước 1. Nếu vẫn dùng dữ liệu có sẵn, đi tới bước 3

### 1. Lấy dữ liệu từ ESCO
- Đảm bảo Dart đã được cài đặt
- Đi đến thư mục [fetch-esco](fetch-esco)
- Cài đặt dependencies cho Dart
```
dart pub get
```
- Chạy code
```
dart run
```

Dữ liệu được ghi vào thử mục `data/`
- `data/data.json`: danh sách job
- `data/knowledge.json`: Danh sách knowledges độc nhất
- `data/skill.json`: Danh sách skill độc nhất

### 2. Chuẩn bị assets
- Quay về thư mục gốc
- Chạy code
```
python ./make-assets/make-assets.py
```
Trên Linux có thể phải chạy bằng lệnh `python3`

Bước này thực hiện: 
- chép data được lấy từ ESCO vào thư mục `assets`
- Tạo sinh thêm nội dung, sử dụng LLM, ghi vào file `assets/knowledge.txt`

### 3. Run
- Quay về thư mục gốc
- Chạy code 
```
python ./src/main_app.py
```
Trên Linux có thể phải chạy bằng lệnh `python3`. Ứng dụng có thể khởi động chậm. Bình tĩnh!

## Giấy phép bản quyền
[MIT License](LICENSE)

## Sử dụng A.I.
- Đồ án này sử dụng Google Gemini (GenAI) để làm giàu dữ liệu jobs và tạo sinh gợi ý project. Tham khảo khảo thêm về Google GenAI API tại [đây](https://ai.google.dev/gemini-api/docs/libraries)
- Gemini 2.5 Flash/Pro, GPT-5 and Claude Sonnet 4.5 LLM trong Github Copilot cho việc hỗ trợ coding

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
