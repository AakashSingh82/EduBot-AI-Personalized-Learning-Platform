# 🎓 EduBot AI — Personalized Learning Platform

> AI-powered personalized learning platform with adaptive lessons, quizzes & tutor chat via Ollama.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![IBM SkillsBuild](https://img.shields.io/badge/IBM-SkillsBuild-054ADA?style=flat-square&logo=ibm)

---

## 📌 Overview

**EduBot AI** is an intelligent, fully local learning platform that adapts to each student's unique learning style, grade level, and knowledge gaps. Powered by **Ollama** (free, no API key required), it delivers personalized lessons, auto-generated quizzes, structured learning paths, and an AI tutor chatbot — all through a clean **Streamlit** web interface.

Built as part of the **IBM SkillsBuild AI-ML Internship Project**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📚 **Adaptive Lessons** | Generates rich, personalized lesson content tailored to learning style (visual, auditory, reading, kinesthetic) |
| ✏️ **Smart Quizzes** | Auto-generates topic quizzes, evaluates answers, and gives per-question feedback with mastery tracking |
| 🗺️ **Learning Paths** | Creates structured multi-week roadmaps toward student-defined learning goals |
| 💬 **AI Tutor Chat** | Context-aware conversational tutor that remembers the full session history |
| 📊 **Progress Tracking** | Tracks quiz scores, completed topics, and mastery levels across sessions |
| 🌍 **Underprivileged Mode** | Prioritizes free and offline-accessible resources for low-income or rural students |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI Backend:** Ollama (Llama 3.2, Mistral, Gemma 2, Phi-3)
- **Language:** Python 3.10+
- **API Compatibility:** OpenAI-compatible via Ollama
- **Deployment:** Streamlit Cloud / Local

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/aakash-singh/edubot-ai.git
cd edubot-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama
Download from [ollama.com](https://ollama.com) and pull a model:
```bash
ollama pull llama3.2
```

### 4. Start Ollama
```bash
ollama serve
```

### 5. Run the app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser. 🎉

---

## 📁 Project Structure

```
edubot-ai/
├── app.py               # Streamlit web application
├── learning_agent.py    # Core AI agent (Ollama-powered)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🦙 Supported Models

| Model | Pull Command | RAM |
|---|---|---|
| Llama 3.2 ✅ | `ollama pull llama3.2` | ~4 GB |
| Mistral | `ollama pull mistral` | ~6 GB |
| Gemma 2 | `ollama pull gemma2` | ~8 GB |
| Phi-3 Mini | `ollama pull phi3` | ~3 GB |

Switch models live from the sidebar inside the app.

---

## 🧠 How the Agent Works

```python
from learning_agent import PersonalizedLearningAgent, StudentProfile

agent = PersonalizedLearningAgent()

student = StudentProfile(
    name="Aakash", age=16, grade=10,
    learning_style="visual",
    subjects_of_interest=["Mathematics"],
    weak_areas=["Algebra"],
    strong_areas=["Arithmetic"],
    socioeconomic_context="general",
)

# Generate a lesson
lesson = agent.generate_lesson(student, "Quadratic Equations")

# Evaluate a quiz
result = agent.evaluate_quiz(student, "Quadratic Equations", lesson.quiz, ["A", "B", "C"])

# Chat with the AI tutor
reply = agent.chat_with_student(student, "Can you explain this with a real-life example?")

# Build a 4-week learning path
path = agent.generate_learning_path(student, "Master Grade 10 Math", weeks=4)
```

---

## ☁️ Deploy on Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**
3. Select your fork, branch `main`, file `app.py`
4. Click **Deploy**

> **Note:** Streamlit Cloud does not support local Ollama. For cloud deployment, switch to the Anthropic API or any hosted LLM endpoint in `learning_agent.py`.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` | Run `ollama serve` in a terminal |
| `Model not found` | Run `ollama pull llama3.2` |
| JSON parse errors | Switch to `mistral` — better at structured output |
| Slow responses | Use a smaller model: `ollama pull phi3` |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**Aakash Singh**
IBM SkillsBuild AI-ML Internship Project

---

*Every child deserves to learn. 📚*
