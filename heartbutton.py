# --- CHANGE THIS IN YOUR heartbutton.py FILE ---
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath, QColor, QRegion

class HeartButton(QPushButton):
    def __init__(self, text="", parent=None, size=120):
        super().__init__(text, parent)
        self.setFixedSize(size, size)
        
    def get_heart_path(self, width, height):
        path = QPainterPath()
        path.moveTo(width / 2, height * 0.85)
        path.cubicTo(width * 0.1, height * 0.6, width * 0.0, height * 0.25, width * 0.25, height * 0.15)
        path.cubicTo(width * 0.4, height * 0.1, width * 0.5, height * 0.3, width / 2, height * 0.35)
        path.cubicTo(width * 0.5, height * 0.3, width * 0.6, height * 0.1, width * 0.75, height * 0.15)
        path.cubicTo(width * 1.0, height * 0.25, width * 0.9, height * 0.6, width / 2, height * 0.85)
        return path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = self.get_heart_path(self.width(), self.height())
        
        if self.isDown():
            color = QColor("#00FF00")
        elif self.underMouse():
            color = QColor("#03C03C")
        else:
            color = QColor("#03C03C")
            
        painter.fillPath(path, color)
        
        painter.setPen(Qt.GlobalColor.white)
        # In PySide6, AlignmentFlag behaves exactly the same
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        path = self.get_heart_path(self.width(), self.height())
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)