import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QPushButton, QColorDialog, QFileDialog, QFormLayout,
                             QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QPainterPath, QPolygonF

class StampGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电子章生成器")
        self.resize(800, 600)
        
        # Default settings
        self.current_color = QColor(255, 0, 0)  # Red
        self.stamp_shape = "Circle" # or "Oval"
        
        self.init_ui()
        self.update_preview()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left Control Panel
        control_panel = QWidget()
        form_layout = QFormLayout(control_panel)
        
        # Inputs
        self.text_top_input = QLineEdit("广州顺丰速运有限公司")
        self.text_top_input.textChanged.connect(self.update_preview)
        
        self.text_bottom_input = QLineEdit("") # Default for circle example
        self.text_bottom_input.textChanged.connect(self.update_preview)
        
        self.font_combo = QComboBox()
        self.font_map = {
            "宋体": "SimSun",
            "楷体": "KaiTi",
            "微软雅黑": "Microsoft YaHei",
            "黑体": "SimHei",
            "仿宋": "FangSong",
            "隶书": "LiSu"
        }
        self.font_combo.addItems(self.font_map.keys())
        self.font_combo.setCurrentText("宋体")
        self.font_combo.currentTextChanged.connect(self.update_preview)

        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["圆形 (Circle)", "椭圆 (Oval)"])
        self.shape_combo.currentIndexChanged.connect(self.on_shape_changed)
        
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.setStyleSheet(f"background-color: {self.current_color.name()}; color: white;")
        self.color_btn.clicked.connect(self.choose_color)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 1000)
        self.width_spin.setValue(300)
        self.width_spin.valueChanged.connect(self.update_preview)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 1000)
        self.height_spin.setValue(300)
        self.height_spin.valueChanged.connect(self.update_preview)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 100)
        self.font_size_spin.setValue(30)
        self.font_size_spin.valueChanged.connect(self.update_preview)

        # Add to form
        form_layout.addRow("公司名称 (上):", self.text_top_input)
        form_layout.addRow("底部文字:", self.text_bottom_input)
        form_layout.addRow("字体:", self.font_combo)
        form_layout.addRow("形状:", self.shape_combo)
        form_layout.addRow("宽度:", self.width_spin)
        form_layout.addRow("高度:", self.height_spin)
        form_layout.addRow("字体大小:", self.font_size_spin)
        form_layout.addRow("颜色:", self.color_btn)
        
        # Buttons
        save_btn = QPushButton("保存图片")
        save_btn.clicked.connect(self.save_image)
        form_layout.addRow(save_btn)

        # Right Preview Panel
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.preview_label, 2)

    def on_shape_changed(self, index):
        if index == 0: # Circle
            self.stamp_shape = "Circle"
            self.width_spin.setValue(300)
            self.height_spin.setValue(300)
            # Update default text for demo purposes if needed, but keeping user input is better
        else: # Oval
            self.stamp_shape = "Oval"
            self.width_spin.setValue(400)
            self.height_spin.setValue(280)
            # Oval usually has different bottom text style, handled in paint
            
        self.update_preview()

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "选择印章颜色")
        if color.isValid():
            self.current_color = color
            self.color_btn.setStyleSheet(f"background-color: {self.current_color.name()}; color: white;")
            self.update_preview()

    def update_preview(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.draw_stamp(painter, width, height)
        
        painter.end()
        self.preview_label.setPixmap(pixmap)

    def draw_stamp(self, painter, width, height):
        pen = QPen(self.current_color)
        pen.setWidth(5)
        painter.setPen(pen)
        
        cx, cy = width / 2, height / 2
        
        # 1. Draw Border
        if self.stamp_shape == "Circle":
            radius = min(width, height) / 2 - 10
            painter.drawEllipse(QPointF(cx, cy), radius, radius)
            text_radius = radius - 30 # Text sits inside
        else: # Oval
            rx = width / 2 - 10
            ry = height / 2 - 10
            painter.drawEllipse(QPointF(cx, cy), rx, ry)
            # For oval, we treat it differently
            text_radius_x = rx - 25
            text_radius_y = ry - 25

        # 2. Draw Star
        self.draw_star(painter, cx, cy, min(width, height) / 8)

        # 3. Draw Top Text
        text_top = self.text_top_input.text()
        font_name = self.font_map.get(self.font_combo.currentText(), "SimSun")
        if text_top:
            font = QFont(font_name, self.font_size_spin.value(), QFont.Weight.Bold)
            painter.setFont(font)
            
            if self.stamp_shape == "Circle":
                self.draw_curved_text_circle(painter, text_top, cx, cy, text_radius, -1) # -1 for top (arching up)
            else:
                self.draw_curved_text_oval(painter, text_top, cx, cy, text_radius_x, text_radius_y)

        # 4. Draw Bottom Text
        text_bottom = self.text_bottom_input.text()
        if text_bottom:
            font = QFont(font_name, self.font_size_spin.value(), QFont.Weight.Bold)
            painter.setFont(font)
            
            if self.stamp_shape == "Circle":
                # For circle, bottom text is usually a number, often curved slightly or straight
                # Example 1 shows a number "01426442" which looks curved? Or maybe faint watermark?
                # Let's assume straight or slightly curved. Usually straight or slightly curved upwards.
                # Let's draw it straight for now or slightly curved.
                # Actually standard code stamps often have the code at the bottom curved upwards.
                self.draw_curved_text_circle(painter, text_bottom, cx, cy, text_radius, 1, is_bottom=True)
            else:
                # For oval, "对账专用章" is usually straight at the bottom center
                # Or sometimes "合同专用章"
                # Example 2 shows "对账专用章" straight.
                painter.drawText(QRectF(0, cy + height/4 - 20, width, 40), Qt.AlignmentFlag.AlignCenter, text_bottom)

    def draw_star(self, painter, cx, cy, radius):
        # Draw a 5-pointed star
        points = []
        for i in range(5):
            # Outer point
            angle_deg = 18 + i * 72 + 90 # Start pointing up? 
            # 18 degrees offset?
            # Standard star: top point is at -90 degrees (if 0 is right) -> 270 deg
            # PyQt coordinates: 0 is right, 90 is down.
            # We want top point at -90 (or 270).
            # Let's use canonical math:
            # P[i] = (cx + R*cos(a), cy + R*sin(a))
            # Angles: -90, -18, 54, 126, 198
            
            # Outer points
            outer_angle = math.radians(-90 + i * 72)
            points.append(QPointF(cx + radius * math.cos(outer_angle), 
                                  cy + radius * math.sin(outer_angle)))
            
            # Inner points
            inner_radius = radius * 0.382 # Golden ratio related
            inner_angle = math.radians(-90 + i * 72 + 36)
            points.append(QPointF(cx + inner_radius * math.cos(inner_angle), 
                                  cy + inner_radius * math.sin(inner_angle)))
            
        star_polygon = QPolygonF(points)
        painter.setBrush(self.current_color)
        painter.drawPolygon(star_polygon)
        painter.setBrush(Qt.BrushStyle.NoBrush) # Reset

    def draw_curved_text_circle(self, painter, text, cx, cy, radius, direction, is_bottom=False):
        # direction: -1 for top (arching), 1 for bottom (arching)
        if not text:
            return
            
        total_angle = len(text) * 25 # Heuristic: degrees per char
        # Adjust per font size if needed
        # Better: calculate based on font width?
        # Let's stick to a fixed angle spread for simplicity or calculate based on length.
        
        # Max angle should be around 180 degrees or less.
        if total_angle > 240:
            total_angle = 240
            
        start_angle = -90 - (total_angle / 2) if not is_bottom else 90 - (total_angle / 2)
        if is_bottom:
             # For bottom text, we want it to read left-to-right, but it's at the bottom.
             # If we just rotate, it might be upside down.
             # Standard circular stamps: Bottom numbers are often upright but follow curve?
             # Or upside down?
             # Usually the bottom numbers "012345" are readable if you turn the stamp?
             # No, usually they are readable from the front.
             # Let's look at the example image 1.
             # The faint text "01426442" is at the bottom. It looks readable.
             # So it is curved upwards.
             start_angle = 270 - (total_angle / 2)
        
        angle_per_char = total_angle / (len(text) + 1) # distribute evenly
        
        # Save state
        painter.save()
        painter.translate(cx, cy)
        
        for i, char in enumerate(text):
            # Calculate angle for this char
            # Top text: goes from left to right (angle increases or decreases?)
            # Top: -90 is center. Left is more negative (e.g. -135), Right is less negative (e.g. -45).
            # So we start from start_angle and add.
            
            if not is_bottom:
                # Top text
                # We want the text to be centered at -90 (270)
                # Spread is total_angle.
                # Start = -90 - half_spread
                theta = -90 - (total_angle / 2) + (i + 1) * angle_per_char
            else:
                # Bottom text
                # Center is 90.
                # Start = 90 - half_spread
                theta = 90 - (total_angle / 2) + (i + 1) * angle_per_char

            painter.save()
            painter.rotate(theta)
            
            # Draw text
            # For top text: we translate out to radius.
            # We want the bottom of the text to be at radius? Or baseline?
            # Text is drawn at (0,0) usually.
            
            if not is_bottom:
                painter.translate(0, -radius)
                # Rotate char so it's upright relative to the center?
                # No, standard rotation `theta` makes the X axis point to the char position.
                # If we draw at (0,0), the text runs along the radius line.
                # We want text perpendicular to radius.
                # So we rotate canvas by `theta`. X axis points OUT from center.
                # If we translate(0, -radius), we are at the top (relative to the rotated frame).
                # Actually, standard:
                # Rotate 0 -> Up.
                # We used standard Qt coords: 0 is Right, 90 Down.
                # If theta is -90 (Up).
                # rotate(-90). X points Up.
                # translate(radius, 0).
                # rotate(90). Text is upright.
                
                # Let's simplify.
                # rotate(theta). X axis is pointing in direction of theta.
                # translate(radius, 0) -> Move to the rim.
                # rotate(90) -> Text baseline becomes perpendicular to radius.
                pass
            
            # Let's restart rotation logic to be cleaner.
            painter.restore() # undo char rotation
            
            painter.save()
            painter.rotate(theta + 90) # Rotate so Y axis points along radius?
            # If theta=-90 (Up). rotate(0). X is Right, Y is Down.
            # We want to move Up. translate(0, -radius).
            
            # Let's use translate first then rotate?
            # No, rotate then translate is easier for polar.
            
            painter.rotate(theta + 90) 
            # If theta = -90 (top). rotate(0).
            # We want to draw at (0, -radius).
            
            painter.translate(0, -radius)
            # Now we are at the spot.
            
            # Check orientation
            # If we just drawText now, it's upright?
            # Yes.
            
            # However, for bottom text (theta ~ 90).
            # rotate(180).
            # translate(0, -radius).
            # We are at (0, radius) relative to center? No.
            # rotate(180) flips everything. (0, -radius) becomes (0, radius) in original coords.
            # But the text will be upside down?
            
            if is_bottom:
               # We want the text to be readable.
               # If theta = 90. rotate(180). translate(0, -radius).
               # Text drawn at (0,0) will be upside down relative to screen?
               # Yes.
               # So we need to rotate 180 more?
               pass

            # Let's do it simply
            painter.restore()
            painter.save()
            
            painter.rotate(theta) # X axis points to char location
            
            if not is_bottom:
                painter.translate(radius, 0)
                painter.rotate(90) # Make text perpendicular
            else:
                painter.translate(radius, 0)
                painter.rotate(90) # Text points out
                # But for bottom text to be readable, top of text should point to center?
                # No, usually bottom text is "standing" on the circle (feet to center) or "hanging" (head to center)?
                # Example 1: "01426442" at bottom. 
                # If you rotate the image 180, it reads "01426442".
                # Wait, looking closely at Example 1...
                # The numbers are upright.
                # So if I look at the stamp, the 0 is on the left, 2 on right.
                # They follow the curve.
                # Their feet point OUTWARDS?
                # Let's assume feet point to center for top text.
                # For bottom text, feet usually point to center too if it's a counter-clockwise read?
                # Or feet point OUTWARDS?
                # Let's check the "Starbucks" logo style.
                # Top text: Feet to center.
                # Bottom text: Heads to center (so it's readable left-to-right).
                
                # In Example 1 (Shanghai Shunheng), Top text feet to center.
                # Bottom text (numbers) feet to center? No.
                # If feet were to center, the numbers would be upside down at the bottom.
                # They look upright. So Heads to center.
                painter.rotate(180) 

            # Center text horizontally on the point
            # Measure text width?
            # Just draw centered.
            painter.drawText(QRectF(-50, -50, 100, 100), Qt.AlignmentFlag.AlignCenter, char)
            
            painter.restore()
            
        painter.restore()

    def draw_curved_text_oval(self, painter, text, cx, cy, rx, ry):
        # Top text for oval
        # Similar to circle but radius changes based on angle.
        # r = rx * ry / sqrt((ry*cos(t))^2 + (rx*sin(t))^2)
        
        if not text:
            return
            
        total_angle = 140 # Ovals usually have text spread on the top arc
        angle_per_char = total_angle / (len(text) + 1)
        
        painter.save()
        painter.translate(cx, cy)
        
        for i, char in enumerate(text):
            theta_deg = -90 - (total_angle / 2) + (i + 1) * angle_per_char
            theta_rad = math.radians(theta_deg)
            
            # Calculate radius at this angle for ellipse
            # Ellipse equation in polar: r = (ab) / sqrt((b cos)^2 + (a sin)^2)
            # a = rx, b = ry
            
            r = (rx * ry) / math.sqrt((ry * math.cos(theta_rad))**2 + (rx * math.sin(theta_rad))**2)
            
            painter.save()
            painter.rotate(theta_deg)
            painter.translate(r, 0)
            painter.rotate(90) # Perpendicular
            
            # Scale painter to make text look "normal" even if oval is squashed?
            # Actually, if we just rotate, the text is unskewed.
            # But on an oval, the normal vector isn't exactly radial unless it's a circle.
            # The text should be perpendicular to the TANGENT of the ellipse.
            # Tangent angle phi: tan(phi) = -(b/a) * cot(theta) ?
            # Slope of tangent: dy/dx
            # x = a cos t, y = b sin t
            # dx/dt = -a sin t, dy/dt = b cos t
            # dy/dx = (b cos t) / (-a sin t) = -(b/a) cot t
            # Normal slope = (a/b) tan t
            
            # Let's calculate the correct rotation angle for the text (perpendicular to tangent)
            # Tangent angle
            # dx = -rx * sin(theta)
            # dy = ry * cos(theta)
            # angle of tangent = atan2(dy, dx)
            # angle of normal = angle of tangent - 90 deg
            
            dx = -rx * math.sin(theta_rad)
            dy = ry * math.cos(theta_rad)
            tangent_angle = math.degrees(math.atan2(dy, dx))
            
            # We want text to be perpendicular to tangent, pointing inwards/outwards.
            # Top text feet point to center.
            # So Up points Outward.
            # At Top (-90), Tangent is 0. Up is -90 (Screen Up).
            # Text Up is -Y.
            # If we rotate 0. Text Up is Screen Up.
            # So at Top we want Rotate 0.
            # Tangent is 0. So Rotate Tangent.
            
            painter.restore()
            painter.save()
            
            # Move to position
            x = r * math.cos(theta_rad)
            y = r * math.sin(theta_rad)
            painter.translate(x, y)
            
            # Rotate
            painter.rotate(tangent_angle)
            
            painter.drawText(QRectF(-50, -50, 100, 100), Qt.AlignmentFlag.AlignCenter, char)
            
            painter.restore()
            
        painter.restore()

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "保存印章", "stamp.png", "PNG Images (*.png)")
        if file_path:
            self.preview_label.pixmap().save(file_path)
            QMessageBox.information(self, "成功", "印章已保存！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StampGenerator()
    window.show()
    sys.exit(app.exec())
