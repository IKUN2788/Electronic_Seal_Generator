<img width="1008" height="790" alt="image" src="https://github.com/user-attachments/assets/008c3dea-92a5-47b6-af7b-db967a6e95b4" />

# 使用 PyQt6 开发一个电子章生成器

在日常办公或开发测试中，我们有时需要生成一些电子印章图片用于测试或演示。本文将带你使用 Python 的 GUI 库 PyQt6，从零开始开发一个功能完善的电子章生成器。

## 🎯 功能演示

做出来的效果大概是这样的：
- **实时预览**：修改文字、颜色、形状，右侧实时显示效果。
- **多种形状**：支持圆形公章和椭圆形专用章。
- **自定义参数**：
    - 公司名称（自动弧形排列）
    - 底部编码/文字（如防伪码或“专用章”）
    - 字体选择（支持宋体、楷体、微软雅黑等）
    - 颜色选择（默认为红色）
    - 尺寸调整
- **导出图片**：一键保存为透明背景的 PNG 图片。

## 🛠️ 技术栈

- **语言**: Python 3
- **GUI 框架**: PyQt6
- **绘图核心**: QPainter (Qt 的 2D 绘图引擎)

## 🚀 核心实现思路

### 1. 界面布局
我们使用 `QMainWindow` 作为主窗口，采用 `QHBoxLayout`（水平布局）将窗口分为左右两部分：
- **左侧控制面板**：放置各种输入框、下拉框和按钮，使用 `QFormLayout` 表单布局，整齐美观。
- **右侧预览区**：放置一个 `QLabel`，用于显示生成的印章图片。

### 2. 绘图原理 (QPainter)
这是本项目的核心。我们需要在 `QPixmap` 上进行绘制。

#### 基础形状
- **圆形/椭圆边框**：使用 `painter.drawEllipse()`。
- **五角星**：通过计算 5 个外点和 5 个内点的坐标，构建 `QPolygonF` 多边形，然后用 `painter.drawPolygon()` 绘制。

#### 难点：弧形文字
普通的 `drawText` 只能画水平文字。要实现印章上方的弧形文字，我们需要用到坐标系变换：**平移 (Translate) + 旋转 (Rotate)**。

**算法逻辑**：
1.  计算总的角度跨度（例如圆形印章文字通常跨越 200 度左右）。
2.  计算每个字符的平均角度间隔。
3.  遍历每个字符：
    *   将坐标系原点平移到印章中心 `(cx, cy)`。
    *   旋转坐标系到该字符对应的角度 `theta`。
    *   再次平移 `(radius, 0)`，将原点移动到圆周边缘。
    *   旋转 90 度，让文字垂直于半径方向（即切线方向）。
    *   绘制字符。
    *   **重要**：每次变换后要 `restore()` 恢复坐标系，以免影响下一个字符。

```python
# 核心代码片段：绘制弧形文字
def draw_curved_text_circle(self, painter, text, cx, cy, radius, direction):
    total_angle = len(text) * 25 # 根据字数估算总角度
    start_angle = -90 - (total_angle / 2) # 从左边开始画
    angle_per_char = total_angle / (len(text) + 1)
    
    painter.save()
    painter.translate(cx, cy) # 移到中心
    
    for i, char in enumerate(text):
        theta = start_angle + (i + 1) * angle_per_char
        
        painter.save()
        painter.rotate(theta) # 旋转到对应角度
        painter.translate(radius, 0) # 移到边缘
        painter.rotate(90) # 文字垂直于半径
        
        # 居中绘制字符
        painter.drawText(QRectF(-20, -20, 40, 40), Qt.AlignmentFlag.AlignCenter, char)
        painter.restore()
        
    painter.restore()
```

### 3. 椭圆印章的处理
椭圆的文字排列比圆形更复杂，因为椭圆的半径是变化的。
我们需要根据角度计算椭圆上对应的极径 $r$：

$$ r = \frac{ab}{\sqrt{(b \cos \theta)^2 + (a \sin \theta)^2}} $$

其中 $a$ 是长半轴，$b$ 是短半轴。

此外，文字的旋转角度不能简单地垂直于半径，而应该**垂直于椭圆在该点的切线**。我们需要计算切线的斜率，然后求出法线角度。

## 📝 完整代码结构

项目结构非常简单：
```
.
├── main.py          # 主程序
├── requirements.txt # 依赖 (PyQt6)
└── README.md
```

### 依赖安装
```bash
pip install PyQt6
```

### 运行
```bash
python main.py
```

## 🎨 进阶优化

在开发过程中，我还加入了一些人性化细节：
1.  **字体映射**：将中文名称（如“宋体”）映射到系统字体名（`SimSun`），防止乱码或不生效。
2.  **动态计算**：文字越多，角度跨度自动调整；字体大小也可以微调。
3.  **防锯齿**：开启 `QPainter.RenderHint.Antialiasing`，让线条和文字边缘平滑，不再有锯齿感。

## 📦 总结

通过这个小项目，我们不仅掌握了 PyQt6 的基础控件使用，还深入理解了 2D 绘图中的坐标变换技巧。特别是“弧形文字”的实现，在很多图形处理场景中都非常实用。

如果你对代码感兴趣，可以自己动手试一试，甚至可以尝试添加更多功能，比如：
- 导入 logo 图片作为中心图案
- 支持磨损效果（噪点）
- 导出 SVG 矢量图

---
*注：本项目仅供技术学习交流，请勿用于非法用途。*
