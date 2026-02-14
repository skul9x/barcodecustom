import win32print
import win32ui
import win32con
from PIL import Image, ImageWin
import os
from datetime import datetime
import traceback  # Import traceback to log full errors

class PrinterService:
    # ---- Label dimensions (mm) ----
    LABEL_WIDTH_MM = 50
    LABEL_HEIGHT_MM = 30

    LOG_FILE = "print_debug.log"

    @staticmethod
    def get_printers():
        try:
            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )
            return [p[2] for p in printers]
        except Exception:
            return []

    @staticmethod
    def _write_log(text):
        """Append debug log to Desktop."""
        try:
            log_path = os.path.join(
                os.path.expanduser("~"), "Desktop", PrinterService.LOG_FILE
            )
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception:
            pass

    @staticmethod
    def print_label(pil_image, printer_name):
        log = []
        log.append(f"========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========")
        log.append(f"Printer: {printer_name}")

        try:
            # ---- Step 1: Set paper size via DEVMODE ----
            hPrinter = win32print.OpenPrinter(printer_name)
            devmode = None
            try:
                try:
                    # Get default DEVMODE
                    devmode = win32print.GetPrinter(hPrinter, 2)["pDevMode"]
                    
                    # Log original driver settings
                    log.append(f"Original DEVMODE PaperSize: {devmode.PaperSize}")
                    log.append(f"Original DEVMODE PaperWidth: {devmode.PaperWidth}")
                    log.append(f"Original DEVMODE PaperLength: {devmode.PaperLength}")

                    # Override paper size to our label dimensions
                    # TRICK: Increase logical width (e.g. 54mm) to shift origin left (Negative Offset)
                    devmode.PaperSize = 256  # DMPAPER_USER (custom size)
                    devmode.PaperWidth = (PrinterService.LABEL_WIDTH_MM + 4) * 10   # 540 (Shift left)
                    devmode.PaperLength = PrinterService.LABEL_HEIGHT_MM * 10  # 300
                    devmode.Fields |= (
                        win32con.DM_PAPERSIZE |
                        win32con.DM_PAPERWIDTH |
                        win32con.DM_PAPERLENGTH
                    )
                    log.append(f"Set DEVMODE: PaperSize=USER, Width={devmode.PaperWidth/10}mm, Length={devmode.PaperLength/10}mm (Applied Offset Trick)")
                except Exception as e:
                    log.append(f"WARNING: Failed to modify DEVMODE: {e}")
                    log.append(traceback.format_exc())
                    # If DEVMODE fails, we proceed with default settings (better than crash)
                    devmode = None 
            finally:
                win32print.ClosePrinter(hPrinter)

            # ---- Step 2: Create DC ----
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            
            # Reset DC with modified DEVMODE if available
            if devmode:
                try:
                    hDC.ResetDC(devmode)
                    log.append("ResetDC(devmode) successful")
                except Exception as e:
                    log.append(f"WARNING: ResetDC failed: {e}")

            # ---- Step 3: Read ACTUAL printable area ----
            dpi_x       = hDC.GetDeviceCaps(88)   # LOGPIXELSX
            dpi_y       = hDC.GetDeviceCaps(90)   # LOGPIXELSY
            printable_w = hDC.GetDeviceCaps(8)    # HORZRES
            printable_h = hDC.GetDeviceCaps(10)   # VERTRES
            phys_w_mm   = hDC.GetDeviceCaps(4)    # HORZSIZE
            phys_h_mm   = hDC.GetDeviceCaps(6)    # VERTSIZE
            offset_x    = hDC.GetDeviceCaps(112)  # PHYSICALOFFSETX
            offset_y    = hDC.GetDeviceCaps(113)  # PHYSICALOFFSETY

            log.append(f"Printer DPI: {dpi_x}x{dpi_y}")
            log.append(f"Physical Size: {phys_w_mm}x{phys_h_mm} mm")
            log.append(f"Printable (px): {printable_w}x{printable_h}")
            log.append(f"Margins (px): offsetX={offset_x}, offsetY={offset_y}")
            log.append(f"Original Image: {pil_image.size}")

            # ---- Step 4: Resize image to fill entire printable area ----
            # CRITICAL: Always resize to printable_w/h to avoid clipping
            pil_image = pil_image.resize((printable_w, printable_h), Image.LANCZOS)
            log.append(f"Resized to: {pil_image.size}")

            # ---- Step 5: Print ----
            hDC.StartDoc("Label Print Job")
            hDC.StartPage()

            dib = ImageWin.Dib(pil_image)
            dib.draw(hDC.GetHandleOutput(), (0, 0, printable_w, printable_h))

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()

            log.append(f"Draw Area: (0, 0, {printable_w}, {printable_h})")
            log.append("Status: PRINT SUCCESS")

        except Exception as e:
            log.append(f"CRITICAL ERROR: {e}")
            log.append(traceback.format_exc())
        
        finally:
            log.append("")
            PrinterService._write_log("\n".join(log))
