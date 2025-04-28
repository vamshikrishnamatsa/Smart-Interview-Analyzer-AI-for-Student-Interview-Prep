import streamlit as st
from modules import flow_controller, asr, tts, question_generator, response_analyzer, feedback_generator, report_generator
from modules.resume_parser import extract_resume_text, enhance_resume
from dotenv import load_dotenv
from record_audio import start_recording, stop_recording
import os

load_dotenv()

st.set_page_config(page_title="AI Interviewer", layout="centered")
st.title("🎤 AI-Based Interviewer")

# Session state
if 'flow' not in st.session_state:
    st.session_state.flow = flow_controller.InterviewFlow()

if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

if 'resume_enhancement' not in st.session_state:
    st.session_state.resume_enhancement = None

if 'recording' not in st.session_state:
    st.session_state.recording = False

if 'jd_text' not in st.session_state:
    st.session_state.jd_text = ""

# ==========================
# 📄 Resume Upload & Enhancer
# ==========================
with st.expander("📄 Upload Your Resume (PDF) + Auto Enhancer"):
    resume_file = st.file_uploader("Upload your resume", type=["pdf"])
    if resume_file:
        st.session_state.resume_text = extract_resume_text(resume_file)
        st.success("✅ Resume uploaded and parsed!")

        if st.button("🚀 Enhance Resume"):
            st.session_state.resume_enhancement = enhance_resume(st.session_state.resume_text)
            st.subheader("🧠 AI Resume Feedback")
            st.write(st.session_state.resume_enhancement)

# ==========================
# 📝 Optional Job Description Input
# ==========================
st.subheader("📝 Optional Job Description")
st.session_state.jd_text = st.text_area("Paste the Job Description (JD) here (optional):", height=200)

# ==========================
# 🎯 Interview Setup
# ==========================
domain = st.selectbox("Interview Domain", ["Technical", "HR", "Managerial"])
level = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"])

# Start Interview
if st.button("🚀 Start Interview"):
    question = question_generator.generate_question(
        history=[],
        domain=domain,
        level=level,
        resume_text=st.session_state.resume_text,
        jd_text=st.session_state.jd_text
    )
    st.session_state.flow.set_question(question)
    tts.speak(question)
    st.audio("output.mp3", format="audio/mp3")
    st.info("Please record or upload your answer...")

# ==========================
# 🎙 Answer Input
# ==========================
st.markdown("### 🎙 Answer Input")

# Start recording
if st.button("▶ Start Recording"):
    start_recording()
    st.session_state.recording = True
    st.info("Recording... click 'Stop Recording' to finish.")

# Stop recording
if st.button("⏹ Stop Recording"):
    if st.session_state.recording:
        audio_path = stop_recording()
        st.session_state.recording = False
        st.audio(audio_path, format="audio/wav")
        answer = asr.transcribe_audio(audio_path)
        st.write("🗣 Your Answer:", answer)
        st.session_state.flow.update(answer)

        feedback = response_analyzer.analyze_response(
            st.session_state.flow.current_question, answer
        )
        st.write("📝 Feedback:", feedback)

        next_q = question_generator.generate_question(
            history=st.session_state.flow.history,
            domain=domain,
            level=level,
            performance_feedback=feedback,
            resume_text=st.session_state.resume_text,
            jd_text=st.session_state.jd_text
        )
        st.session_state.flow.set_question(next_q)
        tts.speak(next_q)
        st.audio("output.mp3", format="audio/mp3")

# Upload audio manually
uploaded_audio = st.file_uploader("📤 Upload Answer (.wav)", type=["wav"])
if uploaded_audio:
    answer = asr.transcribe_audio(uploaded_audio)
    st.write("🗣 Your Answer:", answer)
    st.session_state.flow.update(answer)

    feedback = response_analyzer.analyze_response(
        st.session_state.flow.current_question, answer
    )
    st.write("📝 Feedback:", feedback)

    next_q = question_generator.generate_question(
        history=st.session_state.flow.history,
        domain=domain,
        level=level,
        performance_feedback=feedback,
        resume_text=st.session_state.resume_text,
        jd_text=st.session_state.jd_text
    )
    st.session_state.flow.set_question(next_q)
    tts.speak(next_q)
    st.audio("output.mp3", format="audio/mp3")

# ==========================
# 🛑 End Interview & Report
# ==========================
if st.button("🛑 End Interview"):
    final_feedback = feedback_generator.generate_summary(st.session_state.flow.history)
    st.write("📊 Final Feedback:\n", final_feedback)

    # 💼 LinkedIn Summary Suggestion
    linkedin_summary = feedback_generator.generate_linkedin_summary(final_feedback)
    st.subheader("📢 LinkedIn Summary Suggestion")
    st.write(linkedin_summary)

    # 🎯 Personalized Improvement Plan
    improvement_plan = feedback_generator.generate_improvement_plan(final_feedback)
    st.subheader("📚 Personalized Improvement Plan")
    st.write(improvement_plan)

    # 📄 PDF Report Generation
    report_path = report_generator.generate_pdf(
        st.session_state.flow.history,
        final_feedback
    )
    st.success("✅ PDF Report Generated!")
    with open(report_path, "rb") as f:
        st.download_button("📥 Download Report", data=f, file_name="interview_report.pdf")