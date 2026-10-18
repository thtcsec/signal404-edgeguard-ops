# Kịch bản thuyết trình 3 phút (tiếng Việt)

Giọng tự nhiên, tốc độ vừa. Số liệu lấy từ run thật `inc-thermal-edge-001-20261018085058` — nhớ đây là **telemetry giả lập**.

---

**(0:00–0:20) Vấn đề**

Xin chào ban giám khảo, em là thành viên đội Signal404 với dự án EdgeGuard Ops.  
Trên nhà máy, camera AI edge chạy liên tục. Khi GPU nóng và thermal throttling xảy ra, FPS giảm, frame bị drop — thường phát hiện muộn. Câu hỏi của chúng em: làm sao **phát hiện sớm, xử lý an toàn, và chứng minh đã hồi phục**?

**(0:20–0:45) Giải pháp**

EdgeGuard Ops theo vòng Detect → Investigate → Respond → Verify.  
MongoDB Time Series lưu telemetry; aggregation `$setWindowFields` so sánh xu hướng nhiệt và latency, đồng thời kiểm tra mạng không phải nguyên nhân chính.  
Datadog hiển thị metrics, logs và monitor cho cùng một `device_id` / `incident_id`.

**(0:45–1:20) Live anomaly**

Đây là simulator nhiệt. GPU tăng, latency tăng, FPS giảm.  
Trên dashboard EdgeGuard Fleet Operations, các widget GPU, latency, FPS cùng timeline.  
MongoDB đã mở incident thermal — evidence GPU khoảng 85 độ tại thời điểm detect.

**(1:20–1:55) Automated response**

*Nếu đang demo staged:* “Em cố ý khởi động response-worker sau khi monitor Alert, để ban giám khảo thấy ALERT trước — còn vòng poll tự động thì worker có thể chạy sẵn.”  
Response-worker đặt `commanded_profile=safe`, ghi remediation action. Simulator áp dụng và báo `reported_profile=safe`. Chúng em tách commanded và reported để không nhầm telemetry `full` thành bằng chứng đã chạy `safe`.

**(1:55–2:30) Recovery + Datadog**

Recovery không chỉ đếm thời gian: cần telemetry mới và chuỗi mẫu healthy liên tục.  
Monitor Datadog chuyển **ALERT sang OK**. Incident MongoDB **RESOLVED**, remediation **VERIFIED**.  
Trên run đo được: GPU trung bình khoảng 92°C xuống 54°C, latency 177ms xuống 60ms, FPS khoảng 12 lên 18 — trên dữ liệu giả lập.

**(2:30–3:00) Đóng**

MongoDB là hệ thống ghi nhận và xác minh; Datadog là mặt quan sát cho vận hành.  
Chúng em đã khai báo scaffold trước cửa sổ build và công cụ AI trong hồ sơ.  
EdgeGuard Ops chứng minh một vòng sự cố edge thật sự khép kín — Detect, Investigate, Respond, Verify. Cảm ơn ban giám khảo.

---

## Gợi ý nhấn mạnh nếu bị hỏi

- **APM:** đã xác nhận service `edgeguard-telemetry-api` trên Datadog; analyzer/worker cùng wiring nhưng chưa claim đủ ba service trên UI.  
- **MTTA 111 giây:** có trì hoãn worker có chủ đích cho Alert — nói thẳng.  
- **Change stream:** chưa dùng; poll có chủ đích cho demo.
