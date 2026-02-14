from PIL import Image, ImageDraw, ImageFont
import qrcode

class LabelGenerator:
    def __init__(self, width_mm=50, height_mm=30, dpi=300):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.dpi = dpi
        
        # Calculate pixel dimensions
        self.width_px = int((width_mm / 25.4) * dpi)
        self.height_px = int((height_mm / 25.4) * dpi)
        
    def get_fitting_font(self, text, font_path, max_width, initial_size):
        size = initial_size
        while size > 10:
            try:
                font = ImageFont.truetype(font_path, size)
            except:
                return ImageFont.load_default()
            
            # Using getlength or textbbox for precise measurement
            bbox = font.getbbox(text)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                return font
            size -= 2
        return ImageFont.truetype(font_path, 10)

    def generate(self, name, phone, include_qr=True):
        # Create white background
        image = Image.new("RGB", (self.width_px, self.height_px), "white")
        draw = ImageDraw.Draw(image)
        
        # System Fonts
        font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"
        font_path_reg = "C:\\Windows\\Fonts\\arial.ttf"
        
        # AGGRESSIVE OFFSET COMPENSATION (Remain minimal for hardware margin)
        pad_left = 5  # pixels (~0.4mm)
        pad_right = int(self.height_px * 0.15)  # ~4.5mm (Keep right edge safe)
        inner_gap = int(self.height_px * 0.12)  # Breathing room between QR and Text
        
        if include_qr:
            # QR Code on the left - REDUCED SIZE (60% height)
            qr_size = int(self.height_px * 0.6) 
            qr_y = (self.height_px - qr_size) // 2
            
            qr = qrcode.QRCode(box_size=1, border=1)
            qr.add_data(f"TEL:{phone}\nNAME:{name}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size))
            
            # Paste QR almost at the left edge
            image.paste(qr_img, (pad_left, qr_y))
            
            # Text area on the right - EXPANDED
            text_x_start = pad_left + qr_size + inner_gap
            max_text_w = self.width_px - text_x_start - pad_right
            
            # Professional vertical distribution
            name_size = int(self.height_px * 0.3)
            phone_size = int(self.height_px * 0.22)
            text_gap = int(self.height_px * 0.08)
            
            total_text_h = name_size + text_gap + phone_size
            text_y_start = (self.height_px - total_text_h) // 2
            
            # Auto-fit and Draw Name
            name_font = self.get_fitting_font(name, font_path_bold, max_text_w, name_size)
            draw.text((text_x_start, text_y_start), name, font=name_font, fill="black")
            
            # Auto-fit and Draw Phone
            phone_font = self.get_fitting_font(phone, font_path_reg, max_text_w, phone_size)
            draw.text((text_x_start, text_y_start + name_size + text_gap), phone, font=phone_font, fill="black")
        else:
            # Centered Text
            max_text_w = self.width_px - (pad_right * 2)
            
            name_size = int(self.height_px * 0.4)
            phone_size = int(self.height_px * 0.25)
            text_gap = int(self.height_px * 0.1)
            
            name_font = self.get_fitting_font(name, font_path_bold, max_text_w, name_size)
            phone_font = self.get_fitting_font(phone, font_path_reg, max_text_w, phone_size)
            
            total_text_h = name_size + text_gap + phone_size
            text_y_start = (self.height_px - total_text_h) // 2
            
            name_bbox = name_font.getbbox(name)
            name_w = name_bbox[2] - name_bbox[0]
            draw.text(((self.width_px - name_w) // 2, text_y_start), name, font=name_font, fill="black")
            
            phone_bbox = phone_font.getbbox(phone)
            phone_w = phone_bbox[2] - phone_bbox[0]
            draw.text(((self.width_px - phone_w) // 2, text_y_start + name_size + text_gap), phone, font=phone_font, fill="black")
            
        return image
            
        return image

    def generate_calibration_pattern(self):
        # Create white background
        image = Image.new("RGB", (self.width_px, self.height_px), "white")
        draw = ImageDraw.Draw(image)
        
        # Draw 10mm grid
        mm_pixels = int((10 / 25.4) * self.dpi)
        
        # Vertical lines
        for x in range(0, self.width_px, mm_pixels):
            draw.line([(x, 0), (x, self.height_px)], fill="black", width=2)
            draw.text((x + 2, 2), f"{int(x/mm_pixels)*10}", fill="black")
            
        # Horizontal lines
        for y in range(0, self.height_px, mm_pixels):
            draw.line([(0, y), (self.width_px, y)], fill="black", width=2)
            draw.text((2, y + 2), f"{int(y/mm_pixels)*10}", fill="black")
            
        # Border
        draw.rectangle([(0, 0), (self.width_px - 1, self.height_px - 1)], outline="black", width=3)
        
        # Center Info
        font = ImageFont.load_default()
        text = "50x30mm CHECK"
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((self.width_px - w) // 2, (self.height_px - h) // 2), text, font=font, fill="black")
        
        return image

if __name__ == "__main__":
    # Test generation
    gen = LabelGenerator()
    img = gen.generate("NGUYEN VAN A", "0987.654.321")
    img.save("test_label.png")
    print("Test label saved to test_label.png")
