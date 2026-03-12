"""
SDG 4: Quality Education — Streamlit Web App
============================================
Uses Ollama (local, free, no API key needed).

Setup:
  1. pip install -r requirements.txt
  2. Install Ollama: https://ollama.com
  3. ollama pull llama3.2
  4. ollama serve
  5. streamlit run app.py
"""

import streamlit as st
import json
from learning_agent import PersonalizedLearningAgent, StudentProfile

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="EduBot — AI Personalized Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

.hero-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    padding: 2.5rem 2rem; border-radius: 20px; margin-bottom: 2rem;
    text-align: center; border: 1px solid rgba(255,255,255,0.08);
}
.hero-banner h1 { font-size: 2.8rem; font-weight: 800; color: #fff; margin: 0; }
.hero-banner p  { color: #a8b2d8; font-size: 1.1rem; margin: 0.5rem 0 0; }
.sdg-badge {
    display: inline-block; background: #e63946; color: white;
    padding: 4px 14px; border-radius: 20px; font-size: 0.78rem;
    font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 0.8rem;
}
.ollama-badge {
    display: inline-block; background: #22c55e; color: white;
    padding: 4px 14px; border-radius: 20px; font-size: 0.78rem;
    font-weight: 700; letter-spacing: 1px; margin-left: 8px;
}
.card {
    background: #ffffff; border: 1px solid #e8ecf0; border-radius: 16px;
    padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.card-header {
    font-size: 1.05rem; font-weight: 700; color: #1a1a2e;
    margin-bottom: 0.8rem; display: flex; align-items: center; gap: 8px;
}
.metric-box {
    background: linear-gradient(135deg, #4361ee, #7209b7);
    color: white; padding: 1.2rem; border-radius: 14px; text-align: center;
}
.metric-box .num   { font-size: 2rem; font-weight: 800; }
.metric-box .label { font-size: 0.8rem; opacity: 0.85; }
.chat-user {
    background: #4361ee; color: white; padding: 12px 16px;
    border-radius: 18px 18px 4px 18px; margin: 8px 0; max-width: 75%;
    margin-left: auto; font-size: 0.95rem;
}
.chat-bot {
    background: #f0f4ff; color: #1a1a2e; padding: 12px 16px;
    border-radius: 18px 18px 18px 4px; margin: 8px 0; max-width: 80%;
    font-size: 0.95rem; border-left: 3px solid #4361ee;
}
.week-card {
    border-left: 4px solid #4361ee; padding: 12px 16px;
    background: #f8f9ff; border-radius: 0 12px 12px 0; margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────

defaults = {
    "agent": None,
    "student": None,
    "current_lesson": None,
    "chat_history": [],
    "quiz_submitted": False,
    "quiz_result": None,
    "onboarded": False,
    "welcome_data": {},
    "learning_path": None,
    "pending_message": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.agent is None:
    st.session_state.agent = PersonalizedLearningAgent()


# ─────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
  <div>
    <span class="sdg-badge">🌍 SDG 4 — Quality Education</span>
    <span class="ollama-badge">🦙 Powered by Ollama</span>
  </div>
  <h1>🎓 EduBot AI</h1>
  <p>Personalized learning paths — free, local, for every child, everywhere.</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar — Student Profile
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 👤 Student Profile")

    # Model selector
    model_choice = st.selectbox(
        "🦙 Ollama Model",
        ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3", "qwen2.5"],
        help="Make sure you have pulled this model: ollama pull <model>"
    )
    if st.session_state.agent:
        st.session_state.agent.MODEL = model_choice

    st.markdown("---")

    if not st.session_state.student:
        with st.form("profile_form"):
            name  = st.text_input("Full Name", placeholder="e.g. Aarav Kumar")
            col1, col2 = st.columns(2)
            age   = col1.number_input("Age",   6, 18, 12)
            grade = col2.number_input("Grade", 1, 12,  7)

            learning_style = st.selectbox(
                "Learning Style",
                ["visual", "auditory", "reading", "kinesthetic"]
            )
            language = st.selectbox(
                "Language",
                ["English", "Hindi", "Spanish", "French", "Swahili", "Arabic"]
            )
            socioeconomic_context = st.selectbox(
                "Student Context",
                ["general", "underprivileged", "rural"],
                help="Helps tailor resource recommendations"
            )
            interests = st.multiselect(
                "Subjects of Interest",
                ["Mathematics","Science","English","History","Geography",
                 "Computer Science","Art","Physical Education","Social Studies"],
                default=["Mathematics","Science"]
            )
            weak_areas = st.multiselect(
                "Areas Needing Support",
                ["Fractions","Algebra","Grammar","Reading Comprehension",
                 "Writing","Problem Solving","Critical Thinking","Geometry"],
                default=["Fractions"]
            )
            strong_areas = st.multiselect(
                "Strong Areas",
                ["Arithmetic","Drawing","Memorization","Oral Communication",
                 "Creative Thinking","Teamwork"],
                default=["Arithmetic"]
            )

            submitted = st.form_submit_button(
                "🚀 Start Learning!", use_container_width=True, type="primary"
            )
            if submitted and name:
                st.session_state.student = StudentProfile(
                    name=name, age=age, grade=grade,
                    learning_style=learning_style,
                    subjects_of_interest=interests,
                    weak_areas=weak_areas,
                    strong_areas=strong_areas,
                    language=language,
                    socioeconomic_context=socioeconomic_context,
                )
                st.session_state.onboarded   = False
                st.session_state.agent.reset_conversation()
                st.rerun()
    else:
        s = st.session_state.student
        st.success(f"👋 Hello, **{s.name}**!")
        st.write(f"**Grade:** {s.grade}  |  **Age:** {s.age}")
        st.write(f"**Style:** {s.learning_style.title()}")
        st.write(f"**Language:** {s.language}")
        st.write(f"**Context:** {s.socioeconomic_context.title()}")

        if s.quiz_scores:
            st.markdown("---")
            st.markdown("**📊 Quiz Scores**")
            for topic, score in s.quiz_scores.items():
                c1, c2 = st.columns([3, 1])
                c1.caption(topic[:22])
                c2.caption(f"**{score}%**")

        if s.completed_topics:
            st.markdown("---")
            st.markdown("**✅ Completed Topics**")
            for t in s.completed_topics[-5:]:
                st.markdown(f"• {t}")

        st.markdown("---")
        if st.button("🔄 New Student", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.session_state.agent = PersonalizedLearningAgent()
            st.rerun()


# ─────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────

if not st.session_state.student:
    st.info("👈 **Fill in the student profile** in the sidebar to get started!")

    col1, col2, col3, col4 = st.columns(4)
    for col, (icon, title, desc) in zip(
        [col1, col2, col3, col4],
        [
            ("🎯", "Adaptive Lessons",   "Tailored to learning style & level"),
            ("✏️", "Smart Quizzes",      "Auto-graded with detailed feedback"),
            ("🗺️", "Learning Paths",     "Goal-oriented multi-week roadmaps"),
            ("💬", "AI Tutor Chat",      "Ask anything, get instant explanations"),
        ]
    ):
        col.markdown(f"""
        <div class="card" style="text-align:center">
            <div style="font-size:2rem">{icon}</div>
            <div class="card-header" style="justify-content:center">{title}</div>
            <p style="color:#666; font-size:0.85rem; margin:0">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="background:#f0fdf4; border-left:4px solid #22c55e; margin-top:1rem">
        <div class="card-header">🦙 Running Locally with Ollama — No API Key Needed!</div>
        <p style="color:#444; margin:0">
            1. Install Ollama from <strong>ollama.com</strong><br>
            2. Run: <code>ollama pull llama3.2</code><br>
            3. Run: <code>ollama serve</code><br>
            4. Select your model in the sidebar and start learning!
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    student = st.session_state.student
    agent   = st.session_state.agent

    # ── Onboarding ────────────────────────────────────────────────────────
    if not st.session_state.onboarded:
        with st.spinner("✨ Preparing your personalized learning experience..."):
            try:
                welcome_json = agent.onboard_student(student)
                st.session_state.welcome_data = json.loads(welcome_json)
                st.session_state.onboarded = True
            except Exception as e:
                st.error(f"Onboarding error: {e}. Make sure Ollama is running (`ollama serve`).")
                st.session_state.onboarded = True

    if st.session_state.welcome_data:
        w = st.session_state.welcome_data
        st.markdown(f"""
        <div class="card" style="border-left:4px solid #4361ee; background:#f8f9ff">
            <div class="card-header">🌟 Welcome, {student.name}!</div>
            <p style="color:#444; margin:0">{w.get('welcome_message','')}</p>
            {f'<p style="color:#4361ee;font-weight:600;margin-top:8px">💪 {w.get("motivational_message","")}</p>'
             if w.get('motivational_message') else ''}
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Learn", "✏️ Quiz", "🗺️ My Path", "💬 Ask Tutor"])


    # ════════════════════════════════════════════════════════════════
    # TAB 1 — LEARN
    # ════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 📚 Start a Lesson")

        c1, c2, c3 = st.columns([3, 1, 1])
        topic      = c1.text_input("What do you want to learn today?",
                                    placeholder="e.g. Fractions, Photosynthesis, World War II...")
        difficulty = c2.selectbox("Difficulty", ["auto","beginner","intermediate","advanced"])
        gen_btn    = c3.button("🚀 Generate", type="primary", use_container_width=True)

        if gen_btn and topic:
            with st.spinner(f"🧠 Crafting a lesson on **{topic}**..."):
                try:
                    lesson = agent.generate_lesson(student, topic, difficulty)
                    st.session_state.current_lesson = lesson
                    st.session_state.quiz_submitted  = False
                    st.session_state.quiz_result     = None
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.current_lesson:
            lesson = st.session_state.current_lesson

            c1, c2 = st.columns([4, 1])
            c1.markdown(f"## 📖 {lesson.topic}")
            c2.markdown(f"""
            <div style="text-align:right;margin-top:8px">
                <span style="background:#e8f4fd;color:#1a6fa0;padding:4px 12px;
                border-radius:20px;font-weight:700;font-size:0.85rem">
                    {lesson.difficulty_level.upper()}
                </span>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <div class="card-header">📝 Lesson Content</div>
                <div style="color:#333;line-height:1.8;white-space:pre-wrap">{lesson.content}</div>
            </div>""", unsafe_allow_html=True)

            if lesson.resources:
                with st.expander("🔗 Free Learning Resources"):
                    for r in lesson.resources:
                        st.markdown(f"• {r}")

            if lesson.next_steps:
                with st.expander("➡️ What to Learn Next"):
                    for s in lesson.next_steps:
                        st.markdown(f"→ {s}")

            st.info("✏️ Go to the **Quiz** tab to test your understanding!")


    # ════════════════════════════════════════════════════════════════
    # TAB 2 — QUIZ
    # ════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### ✏️ Knowledge Check")

        if not st.session_state.current_lesson:
            st.info("👆 Generate a lesson in the **Learn** tab first, then come back to quiz!")
        else:
            lesson = st.session_state.current_lesson
            quiz   = lesson.quiz

            if not quiz:
                st.warning("No quiz questions available for this lesson.")
            else:
                st.markdown(f"**Topic:** {lesson.topic} &nbsp;|&nbsp; **Questions:** {len(quiz)}")
                st.markdown("---")

                if not st.session_state.quiz_submitted:
                    with st.form("quiz_form"):
                        student_answers = []
                        for i, q in enumerate(quiz):
                            st.markdown(f"**Q{i+1}. {q['question']}**")
                            options = q.get("options", [])
                            if options:
                                ans = st.radio(
                                    f"q{i}", options,
                                    key=f"q_{i}", label_visibility="collapsed"
                                )
                                student_answers.append(ans[0] if ans else "A")
                            st.markdown("")

                        if st.form_submit_button("📤 Submit Quiz", type="primary", use_container_width=True):
                            with st.spinner("🔍 Evaluating..."):
                                try:
                                    result = agent.evaluate_quiz(
                                        student, lesson.topic, quiz, student_answers
                                    )
                                    st.session_state.quiz_result    = result
                                    st.session_state.quiz_submitted = True
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

                else:
                    result = st.session_state.quiz_result
                    if result:
                        score = result.get("score", 0)

                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"""
                        <div class="metric-box"><div class="num">{score}%</div>
                        <div class="label">Score</div></div>""", unsafe_allow_html=True)
                        c2.markdown(f"""
                        <div class="metric-box" style="background:linear-gradient(135deg,#f72585,#b5179e)">
                        <div class="num">{result.get('correct_count',0)}/{result.get('total_questions',0)}</div>
                        <div class="label">Correct</div></div>""", unsafe_allow_html=True)
                        c3.markdown(f"""
                        <div class="metric-box" style="background:linear-gradient(135deg,#4cc9f0,#4361ee)">
                        <div class="num">{result.get('mastery_level','N/A').title()}</div>
                        <div class="label">Mastery</div></div>""", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="card" style="margin-top:1rem;background:#f0fdf4;border-left:4px solid #22c55e">
                            <p style="color:#166534;margin:0">💬 {result.get('overall_feedback','')}</p>
                        </div>""", unsafe_allow_html=True)

                        with st.expander("📋 Detailed Feedback"):
                            for fb in result.get("detailed_feedback", []):
                                icon = "✅" if fb.get("is_correct") else "❌"
                                bg   = "#f0fdf4" if fb.get("is_correct") else "#fef2f2"
                                cl   = "#166534" if fb.get("is_correct") else "#991b1b"
                                st.markdown(f"""
                                <div style="background:{bg};padding:12px;border-radius:10px;margin:8px 0">
                                    <strong>{icon} {fb.get('question','')}</strong><br>
                                    <span style="color:{cl}">Your answer: {fb.get('student_answer','')}</span>
                                    &nbsp;|&nbsp;
                                    <span style="color:#166534">Correct: {fb.get('correct_answer','')}</span><br>
                                    <small style="color:#555">{fb.get('personalized_explanation','')}</small>
                                </div>""", unsafe_allow_html=True)

                        if result.get("next_recommended_topic"):
                            st.info(f"📌 Next Topic: **{result['next_recommended_topic']}**")

                    if st.button("🔄 Retake Quiz"):
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_result    = None
                        st.rerun()


    # ════════════════════════════════════════════════════════════════
    # TAB 3 — LEARNING PATH
    # ════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🗺️ Personalized Learning Path")

        c1, c2, c3 = st.columns([3, 1, 1])
        goal     = c1.text_input("What's your learning goal?",
                                  placeholder="e.g. Master Grade 7 Mathematics")
        weeks    = c2.selectbox("Duration (weeks)", [2, 4, 6, 8], index=1)
        path_btn = c3.button("🗺️ Build Path", type="primary", use_container_width=True)

        if path_btn and goal:
            with st.spinner("🧭 Building your personalized roadmap..."):
                try:
                    path = agent.generate_learning_path(student, goal, weeks)
                    st.session_state.learning_path = path
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.learning_path:
            path = st.session_state.learning_path
            st.markdown(f"## 🎯 Goal: {path.get('goal', goal)}")

            for week_data in path.get("weekly_plan", []):
                wnum = week_data.get("week", "?")
                with st.expander(f"📅 Week {wnum}: {week_data.get('theme','')}", expanded=wnum == 1):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown("**Topics:**")
                        for t in week_data.get("topics", []):
                            st.markdown(f"• {t}")
                        daily = week_data.get("daily_tasks", {})
                        if daily:
                            st.markdown("**Daily Tasks:**")
                            for day, task in daily.items():
                                st.markdown(f"""
                                <div class="week-card"><strong>{day}</strong>: {task}</div>
                                """, unsafe_allow_html=True)
                    with c2:
                        if week_data.get("milestone"):
                            st.markdown(f"""
                            <div class="card" style="background:#fff9ec;border-left:4px solid #f59e0b">
                                <div class="card-header">🏆 Milestone</div>
                                <p style="color:#78350f;margin:0">{week_data['milestone']}</p>
                            </div>""", unsafe_allow_html=True)
                        for res in week_data.get("free_resources", []):
                            st.caption(f"🔗 {res}")

            if path.get("tips_for_success"):
                st.markdown("---")
                st.markdown("### 💡 Tips for Success")
                tips = path["tips_for_success"][:3]
                cols = st.columns(len(tips))
                for i, tip in enumerate(tips):
                    cols[i].markdown(f"""
                    <div class="card"><p style="color:#444;margin:0;font-size:0.9rem">💡 {tip}</p></div>
                    """, unsafe_allow_html=True)

            if path.get("parent_guidance"):
                with st.expander("👨‍👩‍👧 Guidance for Parents/Guardians"):
                    st.write(path["parent_guidance"])


    # ════════════════════════════════════════════════════════════════
    # TAB 4 — CHAT TUTOR
    # ════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 💬 Ask Your AI Tutor")
        st.caption("Ask anything — concepts, homework, curiosity, or study tips!")

        # Display history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin:4px 0">
                    <div class="chat-user">{msg['content']}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin:4px 0">
                    <div class="chat-bot">🤖 {msg['content']}</div>
                </div>""", unsafe_allow_html=True)

        # Quick prompts
        if not st.session_state.chat_history:
            st.markdown("**Quick Questions:**")
            quick = [
                "Explain fractions with a food example",
                "How do plants make food?",
                "Why is math important in real life?",
                "Give me a study tip for tomorrow's test",
            ]
            cols = st.columns(2)
            for i, q in enumerate(quick):
                if cols[i % 2].button(q, key=f"qp_{i}", use_container_width=True):
                    st.session_state.pending_message = q
                    st.rerun()

        # Input
        c1, c2 = st.columns([5, 1])
        user_input = c1.text_input(
            "message", label_visibility="collapsed",
            placeholder="Type your question...",
            value=st.session_state.get("pending_message", ""),
            key="chat_input",
        )
        send = c2.button("Send ➤", type="primary", use_container_width=True)

        if st.session_state.pending_message:
            user_input = st.session_state.pending_message
            st.session_state.pending_message = ""

        if (send or user_input) and str(user_input).strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("🤔 Thinking..."):
                try:
                    reply = agent.chat_with_student(student, user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"⚠️ Error: {e}. Make sure Ollama is running (`ollama serve`)."
                    })
            st.rerun()

        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                agent.reset_conversation()
                st.rerun()


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#999;font-size:0.8rem;padding:1rem 0">
    🌍 <strong>EduBot AI</strong> — Powered by <strong>Ollama</strong> (Local & Free) &nbsp;|&nbsp;
    Built for <strong>SDG 4: Quality Education</strong> &nbsp;|&nbsp;
    Every child deserves to learn 📚
</div>
""", unsafe_allow_html=True)
