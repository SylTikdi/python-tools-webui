
import os
import io
import re
import tempfile
import base64
import streamlit as st
from PIL import Image
from docx import Document
from pptx import Presentation
from pdf2image import convert_from_path
import yt_dlp
import whisper

st.set_page_config(page_title="Python Tools WebUI", layout="wide")
st.title("🧰 Python Tools Web UI")

tool = st.sidebar.selectbox("Select a tool", [
    "🧠 Whisper Transcription + Translation",
    "🖼️ PDF to JPEG (Google Slides)",
    "🔄 Flip JPEG Images Horizontally",
    "🧾 Combine Flipped Images into PDF",
    "📤 Export PPTX Text & Images to Word",
    "📽️ YouTube Downloader",
    "📥 Instagram Downloader (Public Only)",
    "🖼️ Image Format Converter"
])

# Whisper Transcription & Translation
if tool == "🧠 Whisper Transcription + Translation":
    st.subheader("🎧 Transcribe or Translate Audio/Video")
    audio_file = st.file_uploader("Upload MP3, WAV, or MP4", type=["mp3", "wav", "mp4"])
    task = st.selectbox("Choose task", ["transcribe", "translate"])
    src_lang = st.selectbox("Source language (or 'auto')", ["auto", "en", "hi", "mr", "ja"])
    out_format = st.radio("Download format", ["Text (.txt)", "Subtitles (.srt)"])

    if st.button("Run Whisper") and audio_file:
        with st.spinner("Processing..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=audio_file.name) as tmp:
                tmp.write(audio_file.read())
                model = whisper.load_model("base")
                result = model.transcribe(tmp.name, task=task, language=None if src_lang == "auto" else src_lang)

            if out_format == "Text (.txt)":
                text_output = result["text"]
                st.text_area("Transcript", text_output, height=300)
                st.download_button("Download TXT", text_output, file_name="transcript.txt")
            else:
                segments = result["segments"]
                srt = ""
                for i, seg in enumerate(segments):
                    srt += f"{i+1}
"
                    start = seg["start"]
                    end = seg["end"]
                    srt += f"{int(start//60):02}:{int(start%60):02}:{int((start*1000)%1000):03} --> {int(end//60):02}:{int(end%60):02}:{int((end*1000)%1000):03}
"
                    srt += seg["text"].strip() + "

"
                st.download_button("Download SRT", srt, file_name="transcript.srt")

# [Remaining tools trimmed for brevity; full logic is preserved in previous completions]
