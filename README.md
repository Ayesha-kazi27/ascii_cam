<div align="center">

# 📸 ASCII Cam
### Transform Everyday Photos into Retro, Sketchy & Text-Based Art

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52.svg?style=for-the-badge&logo=qt&logoColor=white)](https://wiki.qt.io/Qt_for_Python)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Selenium](https://img.shields.io/badge/Automation-Selenium-43B02A.svg?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)

*A desktop image-processing application built with Python that turns standard images into stylized visual formats and web-ready text art.*

[Features](#-filters--features) • [Tech Stack](#-tech-stack) • [Installation](#-quick-start) • [Usage](#-how-to-use)

</div>

---

## 🎨 Filters & Features

ASCII Cam comes packed with **5 distinct processing modes**, allowing you to export both standard images and interactive HTML text-art files:

| Filter | Description | Output Format |
| :--- | :--- | :--- |
| **🎨 ASCII (Color)** | Translates pixel data into vibrant, color-mapped ASCII characters. | `.html` |
| **⠋ Braille Art** | Converts high-detail luminance values into intricate Unicode Braille dot patterns. | `.html` |
| **📼 Vintage** | Applies warm color grading, grain, and retro tone-mapping for a classic film aesthetic. | Image (`.png`/`.jpg`) |
| **✏️ Sketchy** | Uses edge detection and grayscale thresholding to create dramatic pencil-sketch art. | Image (`.png`/`.jpg`) |
| **☁️ Dreamy** | Blends soft Gaussian blurs with bloom lighting for an ethereal, surreal look. | Image (`.png`/`.jpg`) |

---

## 🛠️ Tech Stack

This project combines computer vision, desktop UI frameworks, and browser automation:

* **Core Language:** `Python 3`
* **GUI Framework:** `PySide6` (Qt for Python) for a clean, responsive desktop experience.
* **Image Processing:** 
  * `OpenCV` (`cv2`) for matrix operations, edge detection (Sketchy), and blur pipelines (Dreamy).
  * `Mahotas` for specialized morphological operations and Vintage tone processing.
* **Text Art Engine:** `ascii_magic` & custom Unicode Braille mapping algorithms.
* **Automation:** `Selenium` for automated HTML rendering, previewing, and capture workflows.

---

## 🚀 Quick Start

Follow these steps to get **ASCII Cam** running locally on your machine.

### 1. Prerequisites
Ensure you have **Python 3.8+** installed, along with a compatible browser driver (e.g., ChromeDriver) if using Selenium capture features.

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/ascii-cam.git
cd ascii-cam
```

### 3. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install PySide6 opencv-python mahotas ascii_magic selenium numpy
```

### 5. Launch the App
```bash
python main.py
```
*(Note: Replace `main.py` with your actual entry-point filename if different).*

---

## 📖 How to Use

1. **Launch** the ASCII Cam desktop interface.
2. **Load an Image** (or capture via webcam, depending on your setup).
3. **Select a Filter** from the 5 available modes (`ASCII`, `Braille`, `Vintage`, `Sketchy`, or `Dreamy`).
4. **Preview & Export:** 
   * Standard visual filters can be saved directly as image files.
   * `ASCII` and `Braille` modes generate standalone `.html` files that preserve color and formatting in any web browser.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request if you have ideas for new filters or UI enhancements.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFilter`)
3. Commit your Changes (`git commit -m 'Add cool new filter'`)
4. Push to the Branch (`git push origin feature/NewFilter`)
5. Open a Pull Request

---

<div align="center">
  <sub>Built with ❤️ and Python</sub>
</div>
