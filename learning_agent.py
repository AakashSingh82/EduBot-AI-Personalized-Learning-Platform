"""
SDG 4: Quality Education — AI-Powered Personalized Learning Agent
=================================================================
Uses Ollama (local, free, no API key) as the AI backbone.
Setup:
  1. Install Ollama: https://ollama.com
  2. Pull a model:   ollama pull llama3.2
  3. Start Ollama:   ollama serve
"""

from openai import OpenAI
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ─────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────

@dataclass
class StudentProfile:
    name: str
    age: int
    grade: int
    learning_style: str          # visual / auditory / reading / kinesthetic
    subjects_of_interest: list[str]
    weak_areas: list[str]
    strong_areas: list[str]
    language: str = "English"
    socioeconomic_context: str = "general"   # general / underprivileged / rural
    completed_topics: list[str] = field(default_factory=list)
    quiz_scores: dict = field(default_factory=dict)
    session_history: list[dict] = field(default_factory=list)


@dataclass
class LearningSession:
    topic: str
    content: str
    quiz: list[dict]
    resources: list[str]
    next_steps: list[str]
    difficulty_level: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ─────────────────────────────────────────────
# Core AI Learning Agent (Ollama)
# ─────────────────────────────────────────────

class PersonalizedLearningAgent:
    """
    AI agent for personalized education using Ollama (free, local, no API key).
    """

    # ── Change this to any model you have pulled ──────────────────────────
    MODEL = "llama3.2:latest"   # Options: mistral, gemma2, phi3, llama3.1, etc.

    SYSTEM_PROMPT = """You are EduBot — a compassionate, world-class AI tutor specialized in 
personalized education for children and students, with special focus on underprivileged learners.

Your core responsibilities:
1. ASSESS the student's current knowledge level through gentle, encouraging questions.
2. ADAPT your teaching style to the student's learning preferences (visual, auditory, reading/writing, kinesthetic).
3. CREATE engaging, age-appropriate learning content that connects to real-life examples.
4. GENERATE quizzes that are fair, progressive, and build confidence.
5. RECOMMEND free/accessible resources (especially for underprivileged students).
6. CELEBRATE progress and maintain student motivation at all times.
7. USE simple language with local/relatable examples when needed.
8. DETECT gaps in understanding and address them patiently.

When responding in JSON: return ONLY the raw JSON object. No markdown, no code fences, 
no explanation. Start with { and end with }.
Be warm, encouraging, and never condescending."""

    def __init__(self):
        # Ollama uses an OpenAI-compatible API on localhost:11434
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",   # required by the library but ignored by Ollama
        )
        self.conversation_history: list[dict] = []

    # ── 1. Onboard a new student ──────────────────────────────────────────

    def onboard_student(self, profile: StudentProfile) -> str:
        prompt = f"""
A new student has joined. Create a warm welcome and initial learning roadmap.

Student Profile:
{json.dumps(asdict(profile), indent=2)}

Return ONLY this JSON (no markdown, no extra text):
{{
  "welcome_message": "...",
  "initial_assessment_topics": ["topic1", "topic2", "topic3"],
  "recommended_first_lesson": "...",
  "motivational_message": "...",
  "study_schedule_suggestion": "..."
}}
"""
        return self._chat(prompt, expect_json=True)

    # ── 2. Generate a personalized lesson ────────────────────────────────

    def generate_lesson(
        self,
        profile: StudentProfile,
        topic: str,
        difficulty: str = "auto"
    ) -> LearningSession:

        if difficulty == "auto":
            difficulty = self._infer_difficulty(profile, topic)

        prompt = f"""
Create an engaging lesson for this student:

Name: {profile.name}, Age: {profile.age}, Grade: {profile.grade}
Learning Style: {profile.learning_style}
Context: {profile.socioeconomic_context}
Language: {profile.language}
Topic: {topic}
Difficulty: {difficulty}
Weak Areas: {profile.weak_areas}
Previously Completed: {profile.completed_topics}

Return ONLY this JSON (no markdown, no extra text):
{{
  "topic": "{topic}",
  "difficulty_level": "{difficulty}",
  "content": "Full lesson content with examples and analogies tailored to this student...",
  "key_concepts": ["concept1", "concept2"],
  "real_world_connections": ["example1", "example2"],
  "quiz": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A",
      "explanation": "..."
    }},
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "B",
      "explanation": "..."
    }},
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "C",
      "explanation": "..."
    }}
  ],
  "resources": ["Free resource 1", "Free resource 2"],
  "next_steps": ["Next topic 1", "Next topic 2"],
  "encouragement": "Personalized motivational message"
}}

Prioritize free, offline-accessible resources for {profile.socioeconomic_context} context.
"""

        result = self._chat(prompt, expect_json=True)
        data = json.loads(result)

        return LearningSession(
            topic=data.get("topic", topic),
            content=data.get("content", ""),
            quiz=data.get("quiz", []),
            resources=data.get("resources", []),
            next_steps=data.get("next_steps", []),
            difficulty_level=data.get("difficulty_level", difficulty),
        )

    # ── 3. Evaluate a quiz attempt ────────────────────────────────────────

    def evaluate_quiz(
        self,
        profile: StudentProfile,
        topic: str,
        questions: list[dict],
        student_answers: list[str]
    ) -> dict:

        qa_pairs = [
            {
                "question": q["question"],
                "correct_answer": q["correct_answer"],
                "student_answer": a,
                "explanation": q.get("explanation", ""),
            }
            for q, a in zip(questions, student_answers)
        ]

        prompt = f"""
Evaluate this quiz for {profile.name} (Grade {profile.grade}):

Topic: {topic}
Q&A: {json.dumps(qa_pairs, indent=2)}

Return ONLY this JSON (no markdown, no extra text):
{{
  "score": 75,
  "grade": "B",
  "correct_count": 3,
  "total_questions": {len(questions)},
  "detailed_feedback": [
    {{
      "question": "...",
      "is_correct": true,
      "student_answer": "...",
      "correct_answer": "...",
      "personalized_explanation": "..."
    }}
  ],
  "overall_feedback": "Warm encouraging message...",
  "areas_to_review": ["area1"],
  "mastery_level": "developing",
  "next_recommended_topic": "...",
  "badges_earned": ["Great Effort!"]
}}
"""

        result = self._chat(prompt, expect_json=True)
        evaluation = json.loads(result)

        # Update profile
        profile.quiz_scores[topic] = evaluation.get("score", 0)
        if evaluation.get("score", 0) >= 70 and topic not in profile.completed_topics:
            profile.completed_topics.append(topic)

        return evaluation

    # ── 4. Conversational tutoring ────────────────────────────────────────

    def chat_with_student(self, profile: StudentProfile, student_message: str) -> str:

        context = f"""Student context:
Name: {profile.name}, Age: {profile.age}, Grade: {profile.grade}
Learning Style: {profile.learning_style} | Context: {profile.socioeconomic_context}
Interests: {profile.subjects_of_interest} | Weak Areas: {profile.weak_areas}
Recently Completed: {profile.completed_topics[-3:] if profile.completed_topics else []}

Student says: "{student_message}"

Respond as a warm, encouraging tutor. Explain clearly using the student's learning style."""

        self.conversation_history.append({"role": "user", "content": context})

        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + self.conversation_history,
        )

        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": reply})

        profile.session_history.append({
            "timestamp": datetime.now().isoformat(),
            "student": student_message,
            "agent": reply[:200] + "..." if len(reply) > 200 else reply,
        })

        return reply

    # ── 5. Learning path ──────────────────────────────────────────────────

    def generate_learning_path(
        self,
        profile: StudentProfile,
        goal: str,
        weeks: int = 4
    ) -> dict:

        prompt = f"""
Create a {weeks}-week learning path:

Student: {profile.name}, Grade {profile.grade}
Goal: {goal}
Strengths: {profile.strong_areas}
Weak Areas: {profile.weak_areas}
Learning Style: {profile.learning_style}
Context: {profile.socioeconomic_context}
Already Knows: {profile.completed_topics}

Return ONLY this JSON (no markdown):
{{
  "goal": "{goal}",
  "total_weeks": {weeks},
  "weekly_plan": [
    {{
      "week": 1,
      "theme": "...",
      "topics": ["topic1", "topic2"],
      "daily_tasks": {{"Mon": "...", "Tue": "...", "Wed": "...", "Thu": "...", "Fri": "..."}},
      "milestone": "...",
      "free_resources": ["resource1"]
    }}
  ],
  "success_metrics": ["metric1"],
  "tips_for_success": ["tip1", "tip2"],
  "parent_guidance": "How parents can support..."
}}
"""

        result = self._chat(prompt, expect_json=True)
        return json.loads(result)

    # ── 6. Progress report ────────────────────────────────────────────────

    def generate_progress_report(self, profile: StudentProfile) -> dict:

        prompt = f"""
Generate a progress report for:
{json.dumps(asdict(profile), indent=2)}

Return ONLY this JSON (no markdown):
{{
  "student_name": "{profile.name}",
  "report_date": "{datetime.now().strftime('%B %d, %Y')}",
  "overall_progress": "good",
  "progress_percentage": 70,
  "strengths_identified": ["strength1"],
  "areas_needing_attention": ["area1"],
  "quiz_performance_summary": "...",
  "learning_velocity": "moderate",
  "recommended_interventions": ["intervention1"],
  "achievements": ["achievement1"],
  "next_month_goals": ["goal1"],
  "message_to_student": "Encouraging personal message...",
  "message_to_guardian": "Practical guidance for family..."
}}
"""

        result = self._chat(prompt, expect_json=True)
        return json.loads(result)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _chat(self, prompt: str, expect_json: bool = False) -> str:
        system = self.SYSTEM_PROMPT
        if expect_json:
            system += "\n\nCRITICAL: Your entire response must be ONLY a valid JSON object. Do NOT use markdown code fences (```). Do NOT write any text before or after the JSON. Start with { and end with }."

        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content.strip()

        # Robustly strip markdown fences if the model still adds them
        if "```" in raw:
            import re
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                raw = match.group(0)

        return raw

    def _infer_difficulty(self, profile: StudentProfile, topic: str) -> str:
        score = profile.quiz_scores.get(topic)
        if score is None:
            return "beginner"
        if score >= 85:
            return "advanced"
        if score >= 65:
            return "intermediate"
        return "beginner"

    def reset_conversation(self):
        self.conversation_history = []


# ─────────────────────────────────────────────
# CLI Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agent = PersonalizedLearningAgent()

    student = StudentProfile(
        name="Aarav",
        age=12,
        grade=7,
        learning_style="visual",
        subjects_of_interest=["Mathematics", "Science"],
        weak_areas=["Fractions", "Grammar"],
        strong_areas=["Arithmetic", "Drawing"],
        language="English",
        socioeconomic_context="underprivileged",
    )

    print("=" * 60)
    print("🎓 SDG 4 — EduBot AI (Ollama / Local)")
    print("=" * 60)

    print("\n📋 Onboarding student...")
    welcome = agent.onboard_student(student)
    welcome_data = json.loads(welcome)
    print(f"Welcome: {welcome_data.get('welcome_message', '')[:150]}...")

    print("\n📚 Generating lesson on Fractions...")
    lesson = agent.generate_lesson(student, "Introduction to Fractions")
    print(f"Content preview: {lesson.content[:300]}...")
    print(f"Quiz questions: {len(lesson.quiz)}")

    print("\n💬 Chat test...")
    reply = agent.chat_with_student(student, "Why do we need a common denominator?")
    print(f"EduBot: {reply[:200]}...")

    print("\n✅ Done!")
