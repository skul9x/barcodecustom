import customtkinter as ctk
from PIL import Image
from label_maker import LabelGenerator
from printer_service import PrinterService
import threading
import os
from tkinter import messagebox

class LabelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Personal Label Printer (50x30mm)")
        width, height = 850, 600
        self.center_window(width, height)
        
        self.label_gen = LabelGenerator()
        self.current_image = None
        
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Panel: Controls
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.left_panel, text="THÔNG TIN IN TEM", font=("Arial", 20, "bold")).pack(pady=10)
        
        self.name_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Nhập Tên...", height=35)
        self.name_entry.pack(fill="x", padx=20, pady=5)
        self.name_entry.insert(0, "Nguyễn Duy Trường")
        self.name_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        self.phone_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Nhập SĐT...", height=35)
        self.phone_entry.pack(fill="x", padx=20, pady=5)
        self.phone_entry.insert(0, "0388634123")
        self.phone_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        self.qr_var = ctk.BooleanVar(value=True)
        self.qr_cb = ctk.CTkCheckBox(self.left_panel, text="In kèm mã QR", variable=self.qr_var, command=self.update_preview)
        self.qr_cb.pack(pady=5)
        
        ctk.CTkLabel(self.left_panel, text="Chọn máy in:").pack(pady=(10, 0))
        self.printer_list = PrinterService.get_printers()
        self.printer_dropdown = ctk.CTkComboBox(self.left_panel, values=self.printer_list, width=250)
        self.printer_dropdown.pack(pady=5)

        # Scrollable Guide
        ctk.CTkLabel(self.left_panel, text="HƯỚNG DẪN:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.guide_box = ctk.CTkTextbox(self.left_panel, height=120, font=("Arial", 11))
        self.guide_box.pack(fill="x", padx=20, pady=5)
        guide_text = (
            "1. Nhập Tên & SĐT vào ô phía trên.\n"
            "2. Kiểm tra hình ảnh tem ở bên phải.\n"
            "3. 'Auto-fit' sẽ tự co chữ nếu quá dài.\n"
            "4. Đảm bảo máy in GoDEX đã sẵn sàng.\n"
            "5. Chọn đúng tên máy in trong danh sách.\n"
            "6. Bấm 'IN NGAY' để xuất tem.\n"
            "--- Cảm ơn anh đã sử dụng! ---"
        )
        self.guide_box.insert("0.0", guide_text)
        self.guide_box.configure(state="disabled")
        
        self.print_btn = ctk.CTkButton(self.left_panel, text="🖨️ IN NGAY", command=self.print_now, 
                                      fg_color="#2ecc71", hover_color="#27ae60", height=45, font=("Arial", 16, "bold"))
        self.print_btn.pack(pady=(10, 0), fill="x", padx=20)

        # Save Preview Button
        self.save_btn = ctk.CTkButton(self.left_panel, text="💾 Lưu Preview (Desktop)", command=self.save_preview,
                                      fg_color="#3498db", hover_color="#2980b9", height=30, font=("Arial", 11))
        self.save_btn.pack(pady=5, fill="x", padx=50)

        # Debug Button
        self.debug_btn = ctk.CTkButton(self.left_panel, text="📏 In Thước Đo (Debug)", command=self.print_debug,
                                       fg_color="#95a5a6", hover_color="#7f8c8d", height=25, font=("Arial", 11))
        self.debug_btn.pack(pady=(0, 5), fill="x", padx=60)

        # Copyright Footer
        self.footer = ctk.CTkLabel(self.left_panel, text="© 2026 by Nguyễn Duy Trường", font=("Arial", 10), text_color="gray")
        self.footer.pack(side="bottom", pady=5)

        # Right Panel: Preview
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.right_panel, text="XEM TRƯỚC (PREVIEW)", font=("Arial", 14)).pack(pady=10)
        
        self.preview_label = ctk.CTkLabel(self.right_panel, text="", fg_color="gray30")
        self.preview_label.pack(expand=True, padx=20, pady=20)
        
        # Initial call
        self.update_preview()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def update_preview(self):
        name = self.name_entry.get() or "TEN CUA BAN"
        phone = self.phone_entry.get() or "0123.456.789"
        
        self.current_image = self.label_gen.generate(name, phone, self.qr_var.get())
        
        # Resize for display (keep aspect ratio)
        display_w = 400
        display_h = int(display_w * (30/50))
        
        ctk_img = ctk.CTkImage(light_image=self.current_image, 
                               dark_image=self.current_image,
                               size=(display_w, display_h))
        
        self.preview_label.configure(image=ctk_img, text="")
        self.preview_label.image = ctk_img

    def print_now(self):
        printer = self.printer_dropdown.get()
        if not printer:
            print("Chưa chọn máy in!")
            return
            
        def _print_task():
            try:
                PrinterService.print_label(self.current_image, printer)
                print(f"Đã gửi lệnh in tới {printer}")
            except Exception as e:
                print(f"Lỗi khi in: {e}")
                
        threading.Thread(target=_print_task).start()

    def print_debug(self):
        printer = self.printer_dropdown.get()
        if not printer:
            print("Chưa chọn máy in!")
            return
            
        def _print_debug_task():
            try:
                # Generate ruler pattern
                debug_img = self.label_gen.generate_calibration_pattern()
                PrinterService.print_label(debug_img, printer)
                print(f"Đã gửi lệnh in Debug (Thước đo) tới {printer}")
            except Exception as e:
                print(f"Lỗi khi in Debug: {e}")
                
        threading.Thread(target=_print_debug_task).start()

    def save_preview(self):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop, "label_preview.png")
            self.current_image.save(file_path)
            messagebox.showinfo("Thành công", f"Đã lưu ảnh xem trước tại:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {e}")

if __name__ == "__main__":
    app = LabelApp()
    app.mainloop()
