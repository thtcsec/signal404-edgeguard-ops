# Kịch bản thuyết trình 3 phút (tiếng Việt)

Giọng tự nhiên, tốc độ vừa. Số liệu từ run thật `inc-thermal-edge-001-20261018085058` — luôn nhắc đây là **telemetry giả lập (synthetic)**.

Đồng bộ hành động màn hình: [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md).

---

**(0:00–0:20) Vấn đề — slides 1–2**

Xin chào ban giám khảo, em là thành viên đội Signal404 với dự án EdgeGuard Ops.  
Trên nhà máy, camera AI edge chạy liên tục. Khi GPU nóng và thermal throttling xảy ra, FPS giảm — thường phát hiện muộn. Câu hỏi: làm sao **phát hiện sớm, xử lý an toàn, và chứng minh đã hồi phục**?

**(0:20–0:45) Kiến trúc — slide 4**

EdgeGuard Ops theo Detect → Investigate → Respond → Verify.  
MongoDB Time Series là nguồn sự thật; Datadog là mặt quan sát — metrics, logs, monitor theo cùng `device_id` / `incident_id`.

**(0:45–1:05) Anomaly live — simulator**

Đây là simulator nhiệt — dữ liệu synthetic. GPU tăng, latency tăng, FPS giảm.

**(1:05–1:20) Investigate — Datadog dashboard**

Dashboard EdgeGuard Fleet Operations: GPU, latency, FPS.  
MongoDB đã mở incident thermal.

**(1:20–1:30) Alert — monitor + disclosure**

Monitor đang **Alert**. Em **cố ý khởi động response-worker muộn** để ban giám khảo thấy ALERT trước — đây là demo staged, không phải MTTA tự động thuần túy.

**(1:30–1:55) Respond**

Worker đặt `commanded_profile=safe`. Simulator áp dụng và báo `reported_profile=safe`. Chúng em tách commanded và reported để không nhầm telemetry `full` thành bằng chứng đã chạy `safe`.

**(1:55–2:25) Verify**

Recovery cần chuỗi mẫu healthy liên tục, không chỉ đếm giờ.  
Monitor chuyển **ALERT sang OK** — nếu OK chậm hơn kỳ vọng, monitor dùng trung bình ~2 phút; bằng chứng cứng là MongoDB **RESOLVED** / remediation **VERIFIED**.

**(2:25–2:45) Số liệu — slide 7**

Trên run đo được (synthetic): GPU trung bình **92,3°C xuống 54,1°C**, latency **177,3 ms xuống 59,6 ms**, FPS **12,1 lên 18,0**.  
**18 FPS là điểm vận hành safe mode** — đổi peak FPS lấy headroom nhiệt, **không** claim khôi phục đủ khoảng 30 FPS.  
Đồng hồ phát hiện **~40,9 giây** là từ **mẫu telemetry đầu tiên đã lưu** tới lúc detect — không phải từ lúc bắt đầu nóng trong simulator. Khoảng **111 giây** detect→remediate **gồm trì hoãn worker có chủ đích**.

**(2:45–3:00) Đóng — slide 8**

APM live đã xác nhận trên **telemetry-api**.  
EdgeGuard Ops chứng minh vòng Detect → Investigate → Respond → Verify khép kín trên dữ liệu giả lập có nhãn. Cảm ơn ban giám khảo.

---

## Nếu bị hỏi

- **APM ba service:** chỉ claim `edgeguard-telemetry-api` đã thấy trên Datadog.  
- **111 giây / MTTA:** trì hoãn worker có chủ đích — nói thẳng; clip E2E automatic riêng khi worker chạy sẵn.  
- **30 FPS:** không claim; safe mode ≈ 18 FPS sau recovery.  
- **Change stream:** chưa dùng; poll có chủ đích.
