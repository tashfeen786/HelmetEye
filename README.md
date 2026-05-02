# 🪖 HelmetEye — AI-Powered Traffic Surveillance System

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=flat&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black?style=flat&logo=next.js)
![YOLOv12](https://img.shields.io/badge/YOLOv12-Object%20Detection-red?style=flat)
![TypeScript](https://img.shields.io/badge/TypeScript-84%25-blue?style=flat&logo=typescript)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

> 🎓 Final Year Project (FYP) — Bachelor of Information Technology  
> University of Kotli, AJK (2021–2025)

An intelligent real-time traffic surveillance system that automatically 
detects **helmet violations** and **vehicle number plates** from live 
video feeds — built to automate traffic monitoring and support law 
enforcement agencies.

---

## 🚨 Problem Statement

Manual traffic monitoring is:
- ❌ Slow, error-prone, and resource-heavy
- ❌ Unable to scale across multiple camera feeds
- ❌ Inconsistent in catching violations in real-time

**HelmetEye solves this** by using computer vision and deep learning to 
automatically detect violations, extract number plate data, and log 
everything to a database — with zero human intervention.

---

## ✨ Key Features

- 🪖 **Real-time helmet detection** using YOLOv12
- 🔢 **Automatic number plate recognition** via OCR
- 📹 **Live video feed processing** frame by frame
- 🗄️ **Violation logging** with timestamp to database
- ⚡ **FastAPI backend** for fast, scalable API handling
- 💻 **Next.js dashboard** for live monitoring and violation history
- 📊 **Docs folder** with project documentation

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🧠 Detection Model | YOLOv12 |
| 🔤 OCR Engine | EasyOCR / Tesseract |
| ⚙️ Backend | Python, FastAPI |
| 🎨 Frontend | Next.js, TypeScript, Tailwind CSS |
| 🗄️ Database | PostgreSQL / MySQL |
| 👁️ Computer Vision | OpenCV |
| 🚀 Hosting | Firebase App Hosting |

---

## 🏗️ Project Structure
HelmetEye/
│
├── backend/              # Python FastAPI backend
│   ├── models/           # YOLOv12 model files
│   ├── routes/           # API endpoints
│   ├── ocr/              # Number plate OCR logic
│   └── main.py           # FastAPI entry point
│
├── src/                  # Next.js frontend
│   └── app/
│       └── page.tsx      # Main dashboard page
│
├── docs/                 # Project documentation
├── next.config.ts        # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS config
└── apphosting.yaml       # Firebase hosting config

---

## 🔄 How It Works
📹 Live Video Feed
↓
🧠 YOLOv12 Detection (helmet + number plate)
↓
🔤 OCR Engine (extracts plate text)
↓
⚙️ FastAPI Backend (processes & validates)
↓
🗄️ Database (logs violation + timestamp)
↓
💻 Next.js Dashboard (displays live results)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/tashfeen786/HelmetEye.git
cd HelmetEye/backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Go to root directory
cd ..

# Install Node dependencies
npm install

# Start Next.js dev server
npm run dev
```

### Environment Variables

Create a `.env` file in the backend folder:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/helmeteye
MODEL_PATH=./models/yolov12_helmet.pt
```

---

## 📸 Screenshots

<!-- Add your system screenshots here -->
> 🔜 Coming soon — live demo screenshots

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| Detection Model | YOLOv12 |
| Task | Helmet + Number Plate Detection |
| Input | Live video / image frames |
| OCR | Real-time text extraction |

---

## 🎯 Use Cases

- 🏙️ **Smart City Infrastructure** — automated violation detection
- 🚔 **Traffic Law Enforcement** — instant number plate logging  
- 📊 **Road Safety Analytics** — violation trend reporting
- 🏍️ **Highway Monitoring** — large-scale deployment ready

---

## 👨‍💻 Author

**Tashfeen Aziz** — AI/ML Engineer & Python Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/tashfeen-aziz-b51361292)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/tashfeen786)
[![Email](https://img.shields.io/badge/Email-Contact-red?logo=gmail)](mailto:tashfeen247@gmail.com)

---

## 📄 License

This project is licensed under the MIT License.

---

⭐ **If you found this project helpful, please give it a star!**
