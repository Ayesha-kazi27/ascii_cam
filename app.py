from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QKeySequence
from heartbutton import HeartButton
import cv2, os, time, threading
from ascii_magic import AsciiArt
from pathlib import Path
from selenium import webdriver
import mahotas as mh
import numpy as np
from PIL import Image

#will do multithreading se camera n gui dono worrk krega lets do the canmera part here
class Camera(QThread):
    frame_ready = Signal(QImage)
    def __init__(self):
        super().__init__()
        self.running = True
        self.latest_frame = None  # init before run() so it exists even before first frame
        # filter_func: callable(frame_bgr) -> frame_bgr, set by MainWindow.toggle_live_filter.
        # doing the filter math HERE (worker thread) instead of in the GUI slot is what
        # keeps the UI thread free to handle clicks/paints - that's the main fix for lag.
        self.filter_func = None
        self._pending = False  # True while GUI hasn't finished painting the last frame yet
    def run(self):
        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # kam buffer = kam latency
        while self.running:
            ok, frame = cam.read()
            if not ok:
                continue
            self.latest_frame = frame.copy()  # raw frame - filters/save/upload isi pe kaam karte hai

            if self._pending:
                # GUI abhi pichla frame paint kar rahi hai - is frame ko skip karo.
                # agar hum yaha bhi emit karte rehte to Qt ki event queue backlog ho jaati
                # (frames jama hote jaate) aur app dheere dheere aur lag karne lagta.
                continue

            display_frame = frame
            if self.filter_func is not None:
                try:
                    display_frame = self.filter_func(frame)
                except Exception as e:
                    print("Live filter error:", e)
                    display_frame = frame

            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            contiguous_rgb = np.ascontiguousarray(rgb_frame)
            h, w, ch = contiguous_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(
                contiguous_rgb.data, 
                w, 
                h, 
                bytes_per_line, 
                QImage.Format.Format_RGB888
            )
            self._pending = True
            self.frame_ready.emit(qt_image.copy())
        cam.release()
    def frame_delivered(self):
        """called by the GUI slot once it's done with a frame - releases the backpressure"""
        self._pending = False
    def stop(self):
        self.running = False
        self.wait()


class MainWindow (QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ASCII Camera')

        self.msg = False
        self.current_mode = "normal"

        # upload/paste state - jab ye True hoga, live camera feed ignore hoga
        # aur filters is uploaded_frame pe apply honge instead of live cam
        self.uploaded_frame = None
        self.using_upload = False

        container = QWidget()
        self.setCentralWidget(container)
        self.setMinimumSize(600,500)
        #defining layerss hahah
        layoutlvl1 = QVBoxLayout(container)

        layoutlvl2a = QVBoxLayout()
        layoutlvl2b = QHBoxLayout()
        layoutlvl3 = QHBoxLayout()

        layoutlvl1.addLayout(layoutlvl2a)
        layoutlvl1.addLayout(layoutlvl2b)
        layoutlvl2b.addLayout(layoutlvl3)

        #camera haha
        self.camlabel = QLabel('Cam')
        self.camlabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.camlabel.setStyleSheet("background-color: #121212; color: white")
        layoutlvl2a.addWidget(self.camlabel)

        #my fav click button
        click_button = HeartButton()
        layoutlvl2b.addWidget(click_button)
        click_button.clicked.connect(self.click_act)

        #ye doosra row heart button ke right side rakhega naye filters + upload
        layoutlvl3b = QHBoxLayout()
        layoutlvl2b.addLayout(layoutlvl3b)
        
        #ascii wala filter ka button
        ascii = QPushButton('ASCII')
        layoutlvl3.addWidget(ascii)
        ascii.setFixedSize(50, 50)
        ascii.setStyleSheet("""
        QPushButton {
            border-radius: 25px; 
            background-color: #03C03C;
            border: 2px solid #00FF00;
            color: black;
        }
        QPushButton:hover {
            background-color: #3b4b33;
        }
        QPushButton:pressed {
            background-color: #00FF00;
        }
        """)
        ascii.clicked.connect(self.ascii_act)
        
        #vintage filter ka apply  yaha
        vintage = QPushButton('vintage')
        layoutlvl3.addWidget(vintage)
        vintage.setFixedSize(50, 50)
        vintage.setStyleSheet("""
        QPushButton {
            border-radius: 25px; 
            background-color: #03C03C;
            border: 2px solid #00FF00;
            color: black;
        }
        QPushButton:hover {
            background-color: #3b4b33;
        }
        QPushButton:pressed {
            background-color: #00FF00;
        }
        """)
        vintage.clicked.connect(self.vintage_act)

        #braille filter ka button
        braille = QPushButton('Braille')
        layoutlvl3b.addWidget(braille)
        braille.setFixedSize(50, 50)
        braille.setStyleSheet("""
        QPushButton {
            border-radius: 25px; 
            background-color: #03C03C;
            border: 2px solid #00FF00;
            color: black;
        }
        QPushButton:hover {
            background-color: #3b4b33;
        }
        QPushButton:pressed {
            background-color: #00FF00;
        }
        """)
        braille.clicked.connect(self.braille_act)

        #dreamy filter ka button
        dreamy = QPushButton('Dreamy')
        layoutlvl3b.addWidget(dreamy)
        dreamy.setFixedSize(50, 50)
        dreamy.setStyleSheet("""
        QPushButton {
            border-radius: 25px; 
            background-color: #03C03C;
            border: 2px solid #00FF00;
            color: black;
        }
        QPushButton:hover {
            background-color: #3b4b33;
        }
        QPushButton:pressed {
            background-color: #00FF00;
        }
        """)
        dreamy.clicked.connect(self.dreamy_act)

        #img to upload so that u can apply filters to it
        upload_button = QPushButton('Upload')
        layoutlvl3b.addWidget(upload_button)
        upload_button.setFixedSize(80, 40)
        upload_button.setStyleSheet("""
        QPushButton {
            border-radius: 20px; 
            background-color: #03C03C;
            border: 2px solid #00FF00;
            color: black;
            min-height: 40px;
            max-height: 40px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #3b4b33;
        }
        QPushButton:pressed {
            background-color: #00FF00; 
        }
        """)
        upload_button.clicked.connect(self.upload_act)

        #sketchy (b&w) filter ka button
        sketchy = QPushButton('Sketchy')
        layoutlvl3.addWidget(sketchy)
        sketchy.setFixedSize(50, 50)
        sketchy.setStyleSheet("""
        QPushButton {
            border-radius: 25px; 
            background-color: #03C03C;
            border: 2px solid #00FF00;
            color: black;
        }
        QPushButton:hover {
            background-color: #3b4b33;
        }
        QPushButton:pressed {
            background-color: #00FF00;
        }
        """)
        sketchy.clicked.connect(self.sketchy_act)

        #here activate the thread
        self.cam_thread = Camera()
        self.cam_thread.frame_ready.connect(self.update_camera_view)
        self.cam_thread.start()

        # focus chahiye taaki Ctrl+V key events window ko mile
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # registry of toggle-able "live" filters (self.current_mode -> frame_bgr -> frame_bgr)
        # naya continuous filter add karna ho to bas yaha ek entry daal do
        self.live_filters = {
            "vintage": self.apply_vintage,
            "dreamy": self.apply_dreamy,
            "sketchy": self.apply_sketchy,
        }

    # ---------- helpers (reused by camera feed, upload, paste, save) ----------

    def apply_vintage(self, frame_bgr):
        """frame_bgr -> sepia frame_bgr, using mahotas"""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        contiguous_rgb = np.ascontiguousarray(rgb)
        sepia_floats = mh.colors.rgb2sepia(contiguous_rgb)
        sepia_uint8 = np.clip(sepia_floats, 0, 255).astype(np.uint8)
        return cv2.cvtColor(sepia_uint8, cv2.COLOR_RGB2BGR)

    def apply_dreamy(self, frame_bgr):
        """soft glow effect - blend a brightened gaussian blur back over the original"""
        blurred = cv2.GaussianBlur(frame_bgr, (21, 21), 0)
        blurred = cv2.convertScaleAbs(blurred, alpha=1.2, beta=10)
        return cv2.addWeighted(frame_bgr, 0.6, blurred, 0.4, 0)

    def apply_sketchy(self, frame_bgr):
        """black & white threshold using mahotas (image_gray > 125)"""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        contiguous_rgb = np.ascontiguousarray(rgb)
        gray = mh.colors.rgb2gray(contiguous_rgb)
        bw = (gray > 125).astype(np.uint8) * 255
        return cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)

    def display_frame(self, frame_bgr):
        """show a bgr numpy frame on camlabel"""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        contiguous_rgb = np.ascontiguousarray(rgb)
        h, w, ch = contiguous_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            contiguous_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        ).copy()
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.camlabel.width(),
            self.camlabel.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camlabel.setPixmap(scaled_pixmap)

    def refresh_display(self):
        """redraw whatever the current active source is (only needed when
        the live camera thread isn't the one driving the label, i.e. upload mode)"""
        if self.msg:
            return
        if self.using_upload and self.uploaded_frame is not None:
            frame = self.uploaded_frame.copy()
            if self.current_mode in self.live_filters:
                try:
                    frame = self.live_filters[self.current_mode](frame)
                except Exception as e:
                    print(f"{self.current_mode} on uploaded image error:", e)
            self.display_frame(frame)

    def get_current_source_frame(self):
        """returns the frame filters/save should act on: uploaded image if
        one is active, otherwise the live camera's latest frame"""
        if self.using_upload and self.uploaded_frame is not None:
            return self.uploaded_frame.copy()
        elif self.cam_thread.latest_frame is not None:
            return self.cam_thread.latest_frame.copy()
        return None

    def qimage_to_bgr(self, qimage):
        """convert a QImage (e.g. from clipboard) into an opencv BGR numpy array"""
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        width = qimage.width()
        height = qimage.height()
        bytes_per_line = qimage.bytesPerLine()
        buf = qimage.constBits()
        arr = np.frombuffer(buf, dtype=np.uint8, count=height * bytes_per_line)
        arr = arr.reshape((height, bytes_per_line))[:, :width * 3].reshape((height, width, 3))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return np.ascontiguousarray(bgr)

    def open_in_browser(self, file_url):
        """opens a saved file via selenium WITHOUT blocking the GUI thread.
        webdriver.Chrome() + time.sleep(5) used to run straight in the button's
        click handler, which froze the whole window for several seconds every
        single time - running it on a plain background thread fixes that."""
        def worker():
            try:
                driver = webdriver.Chrome()
                driver.get(file_url)
                time.sleep(5)
                driver.quit()
            except Exception as e:
                print("Error opening in browser:", e)
        threading.Thread(target=worker, daemon=True).start()

    # ---------------------------------------------------------------------

    @Slot(QImage)
    def update_camera_view(self, qt_image):
        # is se Camera thread ko pata chal jaata hai ki GUI ne frame le liya,
        # taaki wo agla frame emit kar sake (backpressure release)
        self.cam_thread.frame_delivered()
        # jab upload/paste wali image active hai, live cam feed ko ignore karo
        if self.msg or self.using_upload:
            return
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.camlabel.width(), 
            self.camlabel.height(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camlabel.setPixmap(scaled_pixmap)

    #cutu heart button
    def click_act(self):
        frame_to_save = self.get_current_source_frame()
        if frame_to_save is not None:
            try:
                filename = f"capture_{int(time.time())}.png"

                if self.current_mode in self.live_filters:
                    frame_to_save = self.live_filters[self.current_mode](frame_to_save)
                    print(f"Applying {self.current_mode} filter")

                cv2.imwrite(filename, frame_to_save)

                self.camlabel.clear()
                self.camlabel.setText(f"Snapshot Saved Successfully!\n\n📄 {filename}\n\n(Click anywhere to resume)")
                self.camlabel.setStyleSheet("background-color: #121212; color: #00FF00; font-weight: bold; font-size: 20px;")
                self.camlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msg = True
                print(f"Successfully saved image snapshot asset to: {filename}")
                filepath = Path(filename).resolve().as_uri()
                self.open_in_browser(filepath)
                
            except Exception as e:
                print("Error saving image snapshot:", e)

    #upload button functionality
    def upload_act(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Upload Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not filename:
            return
        frame = cv2.imread(filename)
        if frame is None:
            QMessageBox.warning(self, "Upload Error", "Could not load that image.")
            return
        self.uploaded_frame = frame
        self.using_upload = True
        self.msg = False
        self.camlabel.setStyleSheet("background-color: #121212; color: white")
        self.refresh_display()
        print(f"Uploaded image loaded: {filename}")

    #ctrl+v paste functionality
    def paste_image(self):
        clipboard = QApplication.clipboard()
        qimg = clipboard.image()
        if qimg.isNull():
            print("Clipboard has no image to paste.")
            return
        try:
            frame = self.qimage_to_bgr(qimg)
            self.uploaded_frame = frame
            self.using_upload = True
            self.msg = False
            self.camlabel.setStyleSheet("background-color: #121212; color: white")
            self.refresh_display()
            print("Pasted image from clipboard.")
        except Exception as e:
            print("Error pasting image:", e)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            self.paste_image()
        else:
            super().keyPressEvent(event)

    #ascii filter button functionality
    def ascii_act(self):
        current = self.get_current_source_frame()
        if current is not None:
            try:
                small_frame = cv2.resize(current, (120, 50))
                cv2.imwrite("capture.png", small_frame)
                selfie = AsciiArt.from_image("capture.png")
                selfie.to_html_file("ascii_selfie.html", columns=200, width_ratio=2)
                self.camlabel.clear()
                self.camlabel.setText("Your ASCII selfie is saved as 'ascii_selfie.html'!!!\n\n(Click anywhere to resume)")
                self.camlabel.setStyleSheet("background-color: #121212; color: #00FF00; font-weight: bold; font-size: 20px;")
                self.camlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msg = True
                if os.path.exists("capture.png"):
                    os.remove("capture.png")
            except Exception as e :
                print("error:", e)
                self.msg = True
                self.camlabel.setText("Error applying ASCII filter!")
                self.camlabel.setStyleSheet("background-color: #121212; color: red; font-weight: bold; font-size: 20px;")
                self.camlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                return
        print("ASCII filter applied!")
        #selenoum automation
        if os.path.exists("capture.png"):
            os.remove("capture.png")
        file_url = Path("ascii_selfie.html").resolve().as_uri()
        print(f"Selenium opening: {file_url}")
        self.open_in_browser(file_url)

    #braille filter button functionality
    def braille_act(self):
        current = self.get_current_source_frame()
        if current is not None:
            try:
                rgb = cv2.cvtColor(current, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
                self.generate_braille_html(pil_img, "braille_selfie.html", new_width=120)
                self.camlabel.clear()
                self.camlabel.setText("Your Braille art is saved as 'braille_selfie.html'!!!\n\n(Click anywhere to resume)")
                self.camlabel.setStyleSheet("background-color: #121212; color: #00FF00; font-weight: bold; font-size: 20px;")
                self.camlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msg = True
            except Exception as e:
                print("error:", e)
                self.msg = True
                self.camlabel.setText("Error applying Braille filter!")
                self.camlabel.setStyleSheet("background-color: #121212; color: red; font-weight: bold; font-size: 20px;")
                self.camlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                return
        print("Braille filter applied!")
        #selenoum automation
        file_url = Path("braille_selfie.html").resolve().as_uri()
        print(f"Selenium opening: {file_url}")
        self.open_in_browser(file_url)

    def generate_braille_html(self, img, output_html_path, new_width=100):
        """img: a PIL Image (already RGB) -> colored braille art saved as html"""
        img = img.convert('RGB')

        # Calculate height based on target width and aspect ratio
        # (0.5 multiplier balances the tall layout of Braille text)
        aspect_ratio = img.height / img.width
        new_height = int(new_width * aspect_ratio * 0.5)

        # Resize image so that each 2x4 block matches our structural grid
        img_resized = img.resize((new_width * 2, new_height * 4), Image.Resampling.LANCZOS)

        # Create a grayscale copy specifically for dot thresholding
        img_gray = img_resized.convert('L')
        pixels_gray = img_gray.load()
        pixels_rgb = img_resized.load()

        threshold = 127

        # Build the HTML document structure with CSS
        html_content = ["""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Colored Braille ASCII Art</title>
    <style>
        body {
            background-color: #0b0c10; /* Dark premium background */
            color: #ffffff;
            font-family: monospace;
            font-size: 13px;
            line-height: 1.1;
            letter-spacing: 0.5px;
            text-align: center;
            padding: 40px 10px;
            margin: 0;
        }
        .ascii-container {
            display: inline-block;
            background-color: #020204;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.8);
            border: 1px solid #1f2833;
            white-space: pre; /* Essential to preserve spacing and line breaks */
        }
    </style>
</head>
<body>
    <div class="ascii-container">"""]

        # step through the image in 2x4 pixel blocks
        for y in range(0, img_resized.height, 4):
            row_pieces = []
            for x in range(0, img_resized.width, 2):
                dots = [0] * 8

                # Map pixel luminance to the 8 Braille dot flags
                if pixels_gray[x, y] > threshold:     dots[0] = 1
                if pixels_gray[x, y+1] > threshold:   dots[1] = 1
                if pixels_gray[x, y+2] > threshold:   dots[2] = 1
                if pixels_gray[x, y+3] > threshold:   dots[6] = 1
                if pixels_gray[x+1, y] > threshold:   dots[3] = 1
                if pixels_gray[x+1, y+1] > threshold: dots[4] = 1
                if pixels_gray[x+1, y+2] > threshold: dots[5] = 1
                if pixels_gray[x+1, y+3] > threshold: dots[7] = 1

                # Compute Unicode point
                braille_code = 0x2800
                for i in range(8):
                    if dots[i]:
                        braille_code += (1 << i)

                # Sample the colors inside this 2x4 block to find the average RGB color
                r_total, g_total, b_total = 0, 0, 0
                for dy in range(4):
                    for dx in range(2):
                        r, g, b = pixels_rgb[x+dx, y+dy]
                        r_total += r
                        g_total += g
                        b_total += b

                avg_r = r_total // 8
                avg_g = g_total // 8
                avg_b = b_total // 8

                char = chr(braille_code)

                # Optimization: Use standard spaces for completely empty blocks
                if braille_code == 0x2800:
                    row_pieces.append(" ")
                else:
                    # Wrap character in colored inline span
                    row_pieces.append(f'<span style="color: rgb({avg_r},{avg_g},{avg_b});">{char}</span>')

            html_content.append("".join(row_pieces) + "\n")

        html_content.append("""</div>
</body>
</html>""")

        # Save code to HTML output
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write("".join(html_content))
        print(f"Successfully generated colored Braille art at: {output_html_path}")

    def mousePressEvent(self,event):
        if self.msg:
             self.msg = False
             self.camlabel.setStyleSheet("background-color: #121212; color: white")
             self.camlabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
             self.refresh_display()

    def mouseDoubleClickEvent(self, event):
        # double click cam label to drop the uploaded/pasted image and go back to live cam
        if self.using_upload:
            self.using_upload = False
            self.uploaded_frame = None
            print("Resumed live camera view.")

    #shared toggle for any "live" (continuous) filter - clicking the same
    #filter again turns it off; clicking a different one switches to it
    def toggle_live_filter(self, mode_name):
        if self.current_mode == mode_name:
            self.current_mode = "normal"
            print("Returned to Normal view!")
        else:
            self.current_mode = mode_name
            print(f"{mode_name.capitalize()} filter applied!")
        # camera thread ko batao ki ab konsa filter (agar koi hai) apply karna hai -
        # taaki wo filtering apne thread pe kare, GUI thread ko block kiye bina
        self.cam_thread.filter_func = self.live_filters.get(self.current_mode)
        # agar upload/paste wali image active hai to live feed usko refresh nahi karega,
        # isliye yaha explicitly redraw karo
        if self.using_upload:
            self.refresh_display()

    #vintage filter button functionality
    def vintage_act(self):
        self.toggle_live_filter("vintage")

    #dreamy filter button functionality
    def dreamy_act(self):
        self.toggle_live_filter("dreamy")

    #sketchy (b&w) filter button functionality
    def sketchy_act(self):
        self.toggle_live_filter("sketchy")

    def closeEvent(self, event):
        self.cam_thread.stop()
        event.accept()
    

app = QApplication()
window = MainWindow()
window.show()
app.exec()