import streamlit as st
import tempfile
import os
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
temp_ = "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"

client = OpenAI(api_key=temp_)
# os.getenv("OPENAI_API_KEY")
# )

# Streamlit UI setup
st.set_page_config(page_title="Voice Interview Bot", page_icon="🎙️")
st.title("🎙️ Voice Interview Bot")
st.write("Speak your question. The bot listens until you pause, then responds with voice.")

# Load personal context from info.txt
def load_context(file_path="info.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        st.error("❌ 'info.txt' file not found. Please ensure it exists in the app directory.")
        return None
    except Exception as e:
        st.error(f"❌ Error reading 'info.txt': {e}")
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
    try:
        response = client.responses.create(
            model="gpt-4",
            input=[
                {"role": "system", "content": "You are a skilled interviewee."},
                {"role": "user", "content": prompt},
            ]
        )
        # st.write(response)  
        # print(response) # Debug: Show full response object
        return response.output_text
        # .output_text

    except Exception as e:
        st.error(f"❌ OpenAI API error: {e}")
        return None

# Speak response using gTTS
def speak(text):
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            st.audio(tmp.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Text-to-speech error: {e}")

# Voice input section
st.subheader("🎤 Record Your Question")
if st.button("Start Listening"):
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2
    with sr.Microphone() as source:
        st.info("🔊 Listening... Speak now.")
        try:
            audio = recognizer.listen(source)
            # st.success("🧠 Transcribing...")
            question = recognizer.recognize_google(audio)
            st.write(f"🗣️ You asked: **{question}**")

            context = load_context()
            if context:
                answer = generate_answer(question, context)
                if answer:
                    st.markdown("**🤖 Bot Answer:**")
                    # st.write(answer)
                    speak(answer)

        except sr.UnknownValueError:
            st.error("❌ Could not understand your speech.")
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition error: {e}")