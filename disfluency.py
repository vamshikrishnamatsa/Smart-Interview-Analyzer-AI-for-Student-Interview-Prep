import streamlit as st
import cv2
import numpy as np
import pyaudio
import wave
import threading
import librosa
from deepface import DeepFace
from datetime import datetime
import speech_recognition as sr
from collections import Counter
import re
import google.generativeai as genai

# ========== CONFIGURE GEMINI ==========
api_key = "key value"  # Replace with your Gemini API key
genai.configure(api_key=api_key)

# ========== STREAMLIT SESSION INIT ==========
if "emotions" not in st.session_state:
    st.session_state["emotions"] = []

if "audio_data" not in st.session_state:
    st.session_state["audio_data"] = []

st.set_page_config(page_title="Interview Analyzer", layout="centered")

# ========== Emotion Category Mapping ==========
interview_emotions = {
    "anxious": ["fear", "sad", "disgust"],
    "confused": ["surprise", "sad"],
    "confident": ["happy", "neutral", "surprise"],
    "stressed": ["fear", "sad", "angry"],
    "positive": ["happy", "surprise"],
    "neutral": ["neutral"],
    "sad": ["sad"],
    "angry": ["angry"],
    "happy": ["happy"],
    "surprised": ["surprise"],
    "enthusiastic": ["happy", "surprise", "neutral"],
    "relaxed": ["neutral", "happy"],
    "focused": ["neutral", "confident", "happy"]
}

def categorize_emotion(emotion):
    for category, values in interview_emotions.items():
        if emotion in values:
            return category
    return "Uncategorized"

# ========== AUDIO RECORDING ==========
audio_frames = []

def record_audio(filename="output.wav"):
    global audio_frames
    audio_frames = []

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    FRAMES_PER_BUFFER = 1024
    RECORD_SECONDS = 10

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=FRAMES_PER_BUFFER)

    for _ in range(0, int(RATE / FRAMES_PER_BUFFER * RECORD_SECONDS)):
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        audio_frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

# ========== VIDEO EMOTION DETECTION ==========
def capture_video_emotions(emotion_list, stop_event):
    cap = cv2.VideoCapture(0)
    start_time = datetime.now()

    while (datetime.now() - start_time).seconds < 120:
        ret, frame = cap.read()
        if not ret:
            continue
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            dominant = result[0]['dominant_emotion']
            emotion_list.append(categorize_emotion(dominant))
        except:
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame, channels="RGB", use_column_width=True)

        if stop_event.is_set():
            break
    cap.release()

# ========== AUDIO TONE ANALYSIS ==========
def analyze_audio_tone(file="output.wav"):
    y, sr = librosa.load(file)
    pitch = librosa.yin(y, fmin=50, fmax=300)
    energy = np.mean(librosa.feature.rms(y=y))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Call Gemini to generate personalized feedback
    prompt = f"""
You're a professional voice and communication coach. Given the following voice tone features, generate detailed and unique feedback:
- *Pitch:* {np.mean(pitch):.2f} Hz
- *Energy:* {energy:.4f}
- *Speaking Tempo:* {float(tempo):.2f} BPM

Explain what these metrics suggest about the user's speaking style in a helpful and supportive tone. Suggest how to improve their voice delivery for an interview scenario. Use bullet points or formatting to enhance readability. Make the feedback sound human-written and unique.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        feedback = response.text.strip().split("\n")
    except Exception as e:
        feedback = [f"Feedback generation failed: {e}"]

    return pitch, energy, tempo, feedback

# ========== Speech-to-Text ==========
def audio_to_text(file="output.wav"):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Sorry, there was an issue with the API request."

# ========== Disfluency Removal ==========
def remove_disfluencies(text):
    pattern = r'\b(\w+)\s+\1\b'
    cleaned_text = re.sub(pattern, r'\1', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

# ========== Grammar Correction via Gemini ==========
def correct_grammar(text):
    prompt = f"Correct grammar, spelling, punctuation, and verb tense in this sentence:\n\n\"{text}\"\n\nReturn only the corrected sentence."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Grammar correction failed: {e}"
    
def generate_concise_description(prompt_text):
    short_prompt = f"how to improve this in 6 to 10 words:\n\n{prompt_text}"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(short_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary failed: {e}"
    
def generate_concise_description_1(prompt_text):
    short_prompt = f"how to improve voice in 6 to 10 words:\n\n{prompt_text}"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(short_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary failed: {e}"


# ========== ANALYSIS RESULTS ==========
def analyze_results():
    if st.session_state["emotions"]:
        final_emotion, count = Counter(st.session_state["emotions"]).most_common(1)[0]
        st.subheader("🧍 Facial Emotion")
        st.write(f"*Dominant Emotion:* {final_emotion.capitalize()} (Detected in {count} frames)")

        emotion_summary_prompt = f"The user's facial expression mostly showed '{final_emotion}'. Write a 6-10 word description suitable for an interview feedback report."
        facial_summary = generate_concise_description(emotion_summary_prompt)
        st.write(f"*Summary:* {facial_summary}")
    else:
        st.write("No facial emotion detected.")

    pitch, energy, tempo, feedback = analyze_audio_tone("output.wav")
    st.subheader("🔊 Voice Tone")
    st.write(f"*Pitch:* {np.mean(pitch):.2f} Hz | *Tempo:* {float(tempo):.2f} BPM")

    voice_summary_prompt = f"Pitch: {np.mean(pitch):.2f} Hz, Tempo: {float(tempo):.2f} BPM. Give a short 6-10 word summary describing the speaker's voice tone for interview feedback."
    voice_summary = generate_concise_description_1(voice_summary_prompt)
    st.write(f"*Summary:* {voice_summary}")

    st.subheader("🎙 Transcript")
    transcript = audio_to_text("output.wav")
    st.write(f"*Transcript:* {transcript}")

    st.subheader("📝 Improved Transcript")
    improved_transcript = remove_disfluencies(transcript)
    st.write(f"*Improved:* {improved_transcript}")

    st.subheader("📘 Grammar-Corrected Transcript")
    grammar_corrected = correct_grammar(improved_transcript)
    st.write(f"*Final:* {grammar_corrected}")


# ========== STREAMLIT UI ==========
st.title("🎤 Interview Emotion & Voice Analyzer")
st.markdown("Analyze your facial emotions and voice tone during a simulated interview.")

def start_analysis():
    st.session_state["emotions"] = []
    st.session_state["audio_data"] = []

    stop_event = threading.Event()

    video_thread = threading.Thread(target=capture_video_emotions, args=(st.session_state["emotions"], stop_event))
    audio_thread = threading.Thread(target=record_audio, args=("output.wav",))

    video_thread.start()
    audio_thread.start()

    return stop_event, video_thread, audio_thread

def stop_analysis(stop_event, video_thread, audio_thread):
    stop_event.set()
    video_thread.join()
    audio_thread.join()
    analyze_results()

if "stop_event" not in st.session_state:
    st.session_state["stop_event"] = None
    st.session_state["video_thread"] = None
    st.session_state["audio_thread"] = None

if st.button("🎤 Start Video & Audio Capture Simultaneously"):
    with st.spinner("Starting video and audio capture..."):
        st.session_state["stop_event"], st.session_state["video_thread"], st.session_state["audio_thread"] = start_analysis()

if st.button("🛑 Stop Capture"):
    if st.session_state["stop_event"] and st.session_state["video_thread"] and st.session_state["audio_thread"]:
        with st.spinner("Stopping capture..."):
            stop_analysis(st.session_state["stop_event"], st.session_state["video_thread"], st.session_state["audio_thread"])

if st.session_state["audio_data"]:
    st.audio("output.wav", format="audio/wav")
st.link_button("🔗 Start Interview", "http://localhost:8502")