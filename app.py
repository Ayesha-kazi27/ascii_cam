from PySide6.QtWidgets import *
from PySide6.QtCore import Qt,QThread,Signal,Slot
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from heartbutton import HeartButton
import cv2,sys,os,time
from ascii_magic import AsciiArt
from pathlib import Path
from selenium import webdriver
import mahotas as mh
import numpy as np

#will do multithreading se camera n gui dono worrk krega lets do the canmera part here
class Camera(QThread):
    frame_ready = Signal(QImage)
    def __init__(self):
        super().__init__()
        self.running = True
        self.current_mode = "normal"
    def run(self):
        cam = cv2.VideoCapture(0)
        while self.running:
            _,frame = cam.read()
            if not _:
                continue
            self.latest_frame = frame.copy()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h,w,ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(
                rgb_frame.data, 
                w, 
                h, 
                bytes_per_line, 
                QImage.Format.Format_RGB888
            )
            self.frame_ready.emit(qt_image.copy())
        cam.release()
    def stop(self):
        self.running = False
        self.wait()


class MainWindow (QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ASCII Camera')

        self.msg = False
        self.current_mode = "normal"

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

        #img to upload so that u can apply filters to it
        upload_button = QPushButton('Upload')
        layoutlvl2b.addWidget(upload_button)
        upload_button.setFixedSize(80, 80)
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
        
        #ascii wala filter ka button
        ascii = QPushButton('ASCII')
        layoutlvl3.addWidget(ascii)
        ascii.setFixedSize(70, 70)
        ascii.setStyleSheet("""
        QPushButton {
            border-radius: 30px; 
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
        vintage.setFixedSize(70, 70)
        vintage.setStyleSheet("""
        QPushButton {
            border-radius: 30px; 
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

        #here activate the thread
        self.cam_thread = Camera()
        self.cam_thread.frame_ready.connect(self.update_camera_view)
        self.cam_thread.start()
    @Slot(QImage)
    def update_camera_view(self, qt_image):
        if not self.msg:
            if self.current_mode == "vintage" and self.cam_thread.latest_frame is not None:
                try:
                    
                    current = self.cam_thread.latest_frame.copy()
                    rgb_current = cv2.cvtColor(current, cv2.COLOR_BGR2RGB)
                    
                    contiguous_rgb = np.ascontiguousarray(rgb_current)
                    sepia_floats = mh.colors.rgb2sepia(contiguous_rgb)
                    sepia_uint8 = np.clip(sepia_floats, 0, 255).astype(np.uint8)
                    
                    h, w, ch = sepia_uint8.shape
                    bytes_per_line = ch * w
                    raw_bytes = sepia_uint8.tobytes()
                    
                    qt_image = QImage(
                        raw_bytes, 
                        w, 
                        h, 
                        bytes_per_line, 
                        QImage.Format.Format_RGB888
                    ).copy()
                except Exception as e:
                    print("Live vintage calculation error:", e)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.camlabel.width(), 
            self.camlabel.height(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
            )
            self.camlabel.setPixmap(scaled_pixmap)
    #cutu heart button
    def click_act(self):
        if self.cam_thread.latest_frame is not None:
            try:
                
                filename = f"capture_{int(time.time())}.png"
                
                
                frame_to_save = self.cam_thread.latest_frame.copy()
                
                if self.current_mode == "vintage":
                    
                    rgb_format = cv2.cvtColor(frame_to_save, cv2.COLOR_BGR2RGB)
                    contiguous_rgb = np.ascontiguousarray(rgb_format)
                    
                    # Apply Mahotas lib ka thing
                    sepia_floats = mh.colors.rgb2sepia(contiguous_rgb)
                    sepia_uint8 = np.clip(sepia_floats, 0, 255).astype(np.uint8)
                    
                    # Conversion for cv
                    frame_to_save = cv2.cvtColor(sepia_uint8, cv2.COLOR_RGB2BGR)
                    print(f"Applying vintage filter")

                cv2.imwrite(filename, frame_to_save)
                

                self.camlabel.clear()
                self.camlabel.setText(f"Snapshot Saved Successfully!\n\n📄 {filename}\n\n(Click anywhere to resume)")
                self.camlabel.setStyleSheet("background-color: #121212; color: #00FF00; font-weight: bold; font-size: 20px;")
                self.camlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.msg = True
                print(f"Successfully saved image snapshot asset to: {filename}")
                driver = webdriver.Chrome()
                QApplication.processEvents()
                filepath = Path(filename).resolve().as_uri()
                driver.get(filepath)
                time.sleep(5)
                driver.quite()
                
            except Exception as e:
                print("Error saving image snapshot:", e)
    #upload button functionality
    def upload_act(self):
        pass

    #ascii filter button functionality
    def ascii_act(self):    
        if self.cam_thread.latest_frame is not None:
            try:
                current = self.cam_thread.latest_frame
                small_frame = cv2.resize(current, (120, 50))
                cv2.imwrite("capture.png", small_frame)
                selfie = AsciiArt.from_image("capture.png")
                selfie.to_html_file("ascii_selfie.html", columns=200, width_ratio=2)
                self.camlabel.clear()
                self.camlabel.setText("Your ASCII selfie is saved as 'ascii_selfie.html'!!!")
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
        print("ASCII filter applied!")
        #selenoum automation
        if os.path.exists("capture.png"):
            os.remove("capture.png")
        QApplication.processEvents()
        file_url = Path("ascii_selfie.html").resolve().as_uri()
        print(f"Selenium opening: {file_url}")
        driver = webdriver.Chrome()
        driver.get(file_url)
        time.sleep(5)
        driver.quit()

    def mousePressEvent(self,event):
        if self.msg:
             self.msg = False
             self.camlabel.setStyleSheet("background-color: #121212; color: white")
             self.camlabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
    #vintage filter button functionality
    def vintage_act(self):
        if self.current_mode == "normal":
            self.current_mode = "vintage"
            print("Live Vintage filter applied!")
        else:
            self.current_mode = "normal"
            print("Returned to Live Normal view!")
    def closeEvent(self, event):
        self.cam_thread.stop()
        event.accept()
    

app = QApplication()
window = MainWindow()
window.show()
app.exec()