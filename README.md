# NovaChat AI (Offline Local Model)

NovaChat AI is a complete, standalone general-purpose AI chatbot application that runs **100% locally and offline**.

### 🌟 Key Features
- **Zero API Keys Required:** No Gemini, OpenAI, or external cloud accounts needed.
- **Zero Ollama Required:** Does not require Ollama installation or background services.
- **Offline & Private:** All responses are generated locally on your machine.
- **Multilingual:** Supports questions in English and Tamil.
- **General Knowledge & Math:** Answers definitions, science, tech, math queries, and how-to questions.

---

## 🏗 Project Structure

```
NovaChat-AI/
├── app.py              # Flask server with local offline AI engine
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git exclusion rules
├── README.md           # Instructions
├── templates/
│   └── index.html      # Frontend HTML
└── static/
    ├── css/
    │   └── style.css   # Modern UI styles
    └── js/
        └── script.js   # Client-side Chat UI logic
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
Open a terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
```

### 3. Open in Browser
Navigate to:
👉 **`http://127.0.0.1:5000/`**
