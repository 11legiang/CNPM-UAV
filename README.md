\# Phần mềm phát hiện báo cháy dùng camera UAV



Đồ án cuối kỳ môn Công nghệ phần mềm — Nhóm 11.



\## Thành viên

\- Lê Nguyễn Trường Giang

\- Võ Huy Hùng

\- Nguyễn Bá Minh Nhật



\## Trạng thái hiện tại

\- Đọc và hiển thị video bằng OpenCV.

\- Nhận diện lửa/khói bằng mô hình YOLOv8n có sẵn.

\- Bật cảnh báo CMD sau 5 khung liên tiếp có phát hiện.

\- Tắt trạng thái cảnh báo sau 10 khung liên tiếp không phát hiện.



\## Cài đặt trên Windows CMD

python -m venv .venv

.venv\\Scripts\\activate.bat

python -m pip install -r requirements.txt



\## Chuẩn bị dữ liệu

Tải best.pt từ:

https://huggingface.co/rabahdev/fire-smoke-yolov8n



Đặt tại models/fire\_smoke.pt.



Video thử:

https://www.pexels.com/video/aerial-view-of-forest-fire-with-heavy-smoke-33643174/



Đặt video tại thư mục gốc, tên fire\_test.mp4.



\## Chạy

python detect\_fire.py



Chọn cửa sổ video và nhấn Q để thoát.



\## Giới hạn

\- Dùng video có sẵn để mô phỏng camera UAV.

\- Chưa huấn luyện mô hình riêng.

\- Chưa đánh giá định lượng độ chính xác.

\- Ngưỡng cảnh báo đang tính theo khung hình, chưa theo giây.

\- Chưa có âm thanh, giao diện quản lý và lịch sử cảnh báo.



\## Nguồn và giấy phép

\- Thư viện: https://github.com/ultralytics/ultralytics

\- Mô hình cộng đồng: rabahdev/fire-smoke-yolov8n, công bố AGPL-3.0.

\- Video: theo giấy phép Pexels; xem thông tin tác giả tại trang nguồn.

\- Giấy phép cho mã do nhóm viết sẽ được nhóm thống nhất sau.

