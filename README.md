# Florence-Insight: AI-Powered Image Analysis System

A powerful, local web application for automated image analysis and description using the **Florence-2-base** AI model. This system supports high-speed background processing by leveraging your NVIDIA GPU (CUDA).

![Florence-Insight Demo Screen](static/index.html) <!-- Placeholder for a demo image -->

## 🚀 Key Features
- **Background Processing:** Upload dozens of images and monitor their processing status in real-time without blocking the UI.
- **Analyst Dashboard:** Full control over output length and analysis precision (Beam Search) via global settings.
- **GPU-Powered Inference:** Blazing fast analysis thanks to native CUDA support (works best on GTX 1660 Ti and above).
- **Dark Mode Gallery:** A modern, responsive interface featuring an advanced search for your analyzed images.
- **Privacy First:** The entire model and your database run 100% locally on your machine.

---

## 💻 Technical Requirements (GPU)
For the application to run smoothly and utilize the model's full potential on your GPU:

1. **Hardware:** NVIDIA GPU with at least **6GB VRAM** (e.g., GTX 1660 Ti, RTX 2060+).
2. **Software:** 
   - **Python 3.10** (Recommended for Transformers library consistency).
   - **CUDA Toolkit 12.1+** installed on your system.
3. **Drivers:** Latest NVIDIA Game Ready or Studio Drivers.

### Main Tech Stack:
- **PyTorch 2.2.0+cu121** – Local inference engine with CUDA 12.1 support.
- **Transformers 4.49.0** – Handling the Florence-2 model architecture.
- **Flask** – Lightweight backend server and API.

---

## 🛠 Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUser/Florence-Insight.git
   cd Florence-Insight
   ```

2. **Automated Setup (Recommended):**
   If you have Python 3.10 installed, simply run the setup script:
   ```cmd
   .\install_venv.bat
   ```
   *This script creates the `venv_ai` environment and installs all dependencies, including the specific CUDA-optimized PyTorch binaries.*

3. **Manual Setup:**
   If you prefer manual installation, use the following commands:
   ```bash
   # Install GPU-optimized PyTorch
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   
   # Install other project dependencies
   pip install flask flask-cors transformers einops timm pillow
   ```

---

## 🚦 How to Use

1. **Start the server:**
   Double-click **`run_app.bat`**. This script will:
   - Clean up orphaned Python processes to prevent resource conflicts.
   - Initialize the SQLite database.
   - Automatically download the Florence-2-base model on the first run (approx. 400MB).
   - Start the Flask server with auto-reload enabled.

2. **Open in your browser:**
   Navigate to [**http://localhost:5000**](http://localhost:5000).

3. **Background Batch Analysis:**
   Configure your **AI Profile** in the header, click **"Add New Image"**, and drag your files. The system will enqueue them and process them sequentially in the background while you browse your gallery.

---

## 📄 License
MIT License. Feel free to fork and contribute!
