import streamlit as st
import tempfile
import os
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])



st.set_page_config(page_title="Voice Interview Bot", page_icon="🎙️")
st.title("🎙️ Voice Interview Bot")
st.write("Speak your question. The bot will listen, transcribe, and respond with voice.")


def load_context(file_path="info.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        st.error("'info.txt' file not found. Please ensure it exists in the app directory.")
        return None
    except Exception as e:
        st.error(f" Error reading 'info.txt': {e}")
        return None


def generate_answer(question, context_text):
    prompt = (
        "You are a confident and professional candidate answering an interview question. "
        "Use the personal background below to craft a concise, first-person response:\n\n"
        f"Background:\n{context_text}\n\n"
        f"Question:\n{question}\n\n"
        "Answer clearly and professionally in 3–5 sentences."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a skilled interviewee."},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f" OpenAI API error: {e}")
        return None


def speak(text):
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            st.audio(tmp.name, format="audio/mp3")
    except Exception as e:
        st.error(f" Text-to-speech error: {e}")


st.subheader("🎤 Record Your Question")
# audio_file = st.audio_input("Tap to record your question")
audio_file = st.audio_input("Tap to record")

if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)

    try:
        question = recognizer.recognize_google(audio_data)
        st.success(f" Transcribed Question: {question}")

        context = load_context()
        if context:
            answer = generate_answer(question, context)
            if answer:
                st.markdown("**🤖 Bot Answer:**")
                st.write(answer)
                speak(answer)
    except sr.UnknownValueError:
        st.error(" Could not understand your speech.")
    except sr.RequestError as e:

        st.error(f" Speech recognition error: {e}")

