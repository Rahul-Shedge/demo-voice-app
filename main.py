import streamlit as st
import tempfile
import os
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Voice Interview Bot", page_icon="🎙️")
st.title("🎙️ Voice Interview Bot")
st.write("Record your question below. The bot will respond with voice.")

# Sidebar for personal context
st.sidebar.header("📝 Personal Context")
context_text = st.sidebar.text_area("Paste your resume or background info here", height=200)
if st.sidebar.button("Save Context"):
    st.session_state["context_text"] = context_text
    st.sidebar.success("✅ Context saved!")

# Load context from session or fallback file
def load_context(file_path="info.txt"):
    if "context_text" in st.session_state:
        return st.session_state["context_text"]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None

# Generate answer using OpenAI
def generate_answer(question, context_text):
    prompt = (
        "You are a confident and professional candidate answering an interview question. "
        "Use the personal background below to craft a concise, first-person response:\n\n"
        f"Background:\n{context_text}\n\n"
        f"Question:\n{question}\n\n"
        "Answer clearly and professionally in 3–5 sentences."
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a skilled interviewee."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

# Record and transcribe audio
st.subheader("🎤 Record Your Question")
audio_file = st.audio_input("Speak your question here")

if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)
    try:
        question = recognizer.recognize_google(audio_data)
        st.success(f"🗣️ Transcribed Question: {question}")

        context = load_context()
        if context:
            answer = generate_answer(question, context)
            st.markdown("**🤖 Bot Answer:**")
            st.write(answer)

            tts = gTTS(answer)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                st.audio(tmp.name, format="audio/mp3")
    except sr.UnknownValueError:
        st.error("❌ Could not understand your speech.")
    except sr.RequestError as e:
        st.error(f"❌ Speech recognition error: {e}")