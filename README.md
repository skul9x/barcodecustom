# 🖨️ Phần mềm In Tem Nhãn Cá Nhân (50x30mm)

Phần mềm chuyên dụng để thiết kế và in tem nhãn sticker kích thước **50x30mm**, tối ưu cho máy in mã vạch **GoDEX G500** và các dòng máy in sử dụng Driver Seagull Scientific.

## ✨ Tính năng nổi bật

*   **Thiết kế tem chuẩn:** Tự động tạo bố cục tem gồm QR Code và Thông tin cá nhân (Tên, SĐT).
*   **Cơ chế Bù trừ Offset:** Sử dụng kỹ thuật "Negative Offset" (PaperWidth Trick) để khắc phục lỗi lệch lề trái (10mm) phổ biến trên máy in GoDEX.
*   **Auto-fit Font:** Tự động tính toán và thu nhỏ cỡ chữ nếu tên quá dài, đảm bảo không bị tràn lề.
*   **Lưu Preview:** Chức năng lưu ảnh tem ra Desktop giúp kiểm tra layout trước khi in thật, tránh lãng phí giấy.
*   **Hệ thống Log Debug:** Ghi lại chi tiết thông số Driver (DPI, Printable Area, DEVMODE) ra file `print_debug.log` trên Desktop để hỗ trợ sửa lỗi từ xa.
*   **Giao diện hiện đại:** Xây dựng trên nền tảng `CustomTkinter` với chế độ Dark/Light mode.

## 🛠️ Công nghệ sử dụng

*   **Ngôn ngữ:** Python 3.12+
*   **Giao diện (UI):** `customtkinter`
*   **Xử lý ảnh:** `Pillow` (PIL)
*   **Giao tiếp máy in:** `pywin32` (win32print, win32ui)
*   **Mã QR:** `qrcode`

## ⚙️ Cấu hình Máy in (Driver Settings)

Để phần mềm đạt độ chính xác cao nhất (không bị cắt chữ), anh cần thực hiện cấu hình Driver lần đầu như sau:

1.  Vào **Control Panel** > **Devices and Printers**.
2.  Chuột phải vào máy in (**GoDEX G500**) > Chọn **Printing Preferences**.
3.  Tại tab **Page Setup**:
    *   Bấm vào nút **New...** (hoặc **Edit...**) tại mục **Stock**.
    *   **Name:** Đặt tên là `Sticker 50x30`.
    *   **Type:** Chọn `Die-Cut Labels`.
    *   **Label Size:** Width = `50mm`, Height = `30mm`.
    *   **Exposed Liner Widths:** Left = `0`, Right = `0`.
    *   Bấm **OK**.
4.  Tại mục **Orientation**: Chọn **Portrait** (hoặc Landscape tùy theo cách lắp giấy, phần mềm sẽ tự xoay dựa trên thông số này).
5.  Bấm **Apply** và **OK** để lưu lại.

## 🚀 Cài đặt & Sử dụng

### Dành cho người dùng (Chạy file .exe)
1. Tải file `LabelPrinter.exe` trong thư mục `dist/`.
2. Mở ứng dụng, nhập Tên và Số điện thoại.
3. Chọn máy in (Ví dụ: GoDEX G500) và bấm **IN NGAY**.

### Dành cho lập trình viên (Chạy từ source code)
1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install customtkinter Pillow pywin32 qrcode
   ```
2. Chạy ứng dụng:
   ```bash
   python main.py
   ```

## 📦 Đóng gói ứng dụng (Build .exe)
Sử dụng PyInstaller để đóng gói thành một file duy nhất:
```bash
pyinstaller --noconfirm --onefile --windowed --name "LabelPrinter" --add-data "path/to/customtkinter;customtkinter" main.py
```

## 📝 Lưu ý kỹ thuật cho máy in GoDEX
*   Phần mềm tự động ép Driver về khổ giấy **50x30mm** thông qua API DEVMODE.
*   Để căn giữa tem hoàn hảo, phần mềm sử dụng khổ giấy ảo **54mm** để bù trừ cho khoảng trắng 10mm vật lý của máy in.

---
**Phát triển bởi:** Nguyễn Duy Trường  
**Năm:** 2026
