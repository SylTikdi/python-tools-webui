print("🛠️ Debugging FFmpeg load...")

import os
import re
import tempfile
import shutil
import base64
import streamlit as st
from PIL import Image
from docx import Document
from pptx import Presentation
from pdf2image import convert_from_path
import yt_dlp
import whisper

# === TOOL SELECTION ===
st.title("🧰 Python Tools Web UI")
tool = st.sidebar.selectbox("Select a tool", [
    "🧠 Whisper Transcription + Translation",
    "🖼️ PDF to JPEG (Google Slides)",
    "🔄 Flip JPEG Images Horizontally",
    "🧾 Combine Flipped Images into PDF",
    "📤 Export PPTX Text & Images to Word",
    "📽️ YouTube Downloader",
    "📥 Instagram Downloader (Public Only)"
])

# === 1. Whisper Transcription + Translation ===
if tool == "🧠 Whisper Transcription + Translation":
    st.subheader("Upload audio/video to transcribe or translate")
    uploaded_file = st.file_uploader("Upload MP3, WAV, MP4, etc.", type=["mp3", "wav", "mp4"])
    lang_from = st.selectbox("Source language", ["auto", "en", "hi", "mr", "ja"])
    lang_to = st.selectbox("Translate to", ["None", "en", "hi", "mr", "ja"])
    format_option = st.radio("Output format", ["Plain text (.txt)", "Subtitles (.srt)"])

    if st.button("Transcribe/Translate") and uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
            tmp.write(uploaded_file.read())
            audio_path = tmp.name

        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=None if lang_from == "auto" else lang_from, task="translate" if lang_to != "None" else "transcribe")

        text = result["text"]
        output_data = text
        output_ext = "txt"

        if format_option == "Subtitles (.srt)":
            from datetime import timedelta
            segments = result["segments"]
            srt_output = ""
            for i, seg in enumerate(segments):
                start = str(timedelta(seconds=int(seg["start"])))
                end = str(timedelta(seconds=int(seg["end"])))
                srt_output += f"{i+1}\n{start} --> {end}\n{seg['text']}\n\n"
            output_data = srt_output
            output_ext = "srt"

        st.download_button("📥 Download Result", data=output_data, file_name=f"output.{output_ext}")

# === 2. PDF to JPEG (Google Slides Export) ===
elif tool == "🖼️ PDF to JPEG (Google Slides)":
    st.subheader("Convert PDF to JPEG")
    uploaded_pdf = st.file_uploader("Upload exported Google Slides as PDF", type=["pdf"])
    if st.button("Convert to JPEG") and uploaded_pdf:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_pdf.read())
            tmp_path = tmp.name

        images = convert_from_path(tmp_path)
        output_dir = tempfile.mkdtemp()
        for i, img in enumerate(images):
            img_path = os.path.join(output_dir, f"slide{i+1}.jpg")
            img.save(img_path, "JPEG")
        st.success("✅ Converted!")
        for img_file in sorted(os.listdir(output_dir)):
            with open(os.path.join(output_dir, img_file), "rb") as f:
                st.download_button(f"Download {img_file}", f, file_name=img_file)

# === 3. Flip Images ===
elif tool == "🔄 Flip JPEG Images Horizontally":
    st.subheader("Flip images horizontally")
    uploaded = st.file_uploader("Upload multiple JPEG images", accept_multiple_files=True, type=["jpg", "jpeg"])
    if st.button("Flip Images") and uploaded:
        output_dir = tempfile.mkdtemp()
        for file in uploaded:
            img = Image.open(file)
            flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
            out_path = os.path.join(output_dir, file.name)
            flipped.save(out_path)
            with open(out_path, "rb") as f:
                st.download_button(f"Download {file.name}", f, file_name=file.name)

# === 4. Combine Flipped Images into PDF ===
elif tool == "🧾 Combine Flipped Images into PDF":
    st.subheader("Combine JPEGs into PDF (in order)")
    uploaded = st.file_uploader("Upload flipped JPEG images", accept_multiple_files=True, type=["jpg", "jpeg"])
    if st.button("Create PDF") and uploaded:
        def natural_sort_key(s):
            return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s.name)]
        files_sorted = sorted(uploaded, key=natural_sort_key)

        image_list = []
        for file in files_sorted:
            img = Image.open(file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image_list.append(img)

        first_image = image_list.pop(0)
        pdf_path = tempfile.mktemp(suffix=".pdf")
        first_image.save(pdf_path, save_all=True, append_images=image_list)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name="combined_output.pdf")

# === 5. PPTX to Word Export ===
elif tool == "📤 Export PPTX Text & Images to Word":
    st.subheader("Convert PowerPoint to Word")
    uploaded_ppt = st.file_uploader("Upload PPTX file", type=["pptx"])
    if st.button("Convert to Word") and uploaded_ppt:
        try:
            prs = Presentation(uploaded_ppt)
            doc = Document()
            for i, slide in enumerate(prs.slides):
                doc.add_heading(f"Slide {i+1}", level=1)
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        doc.add_paragraph(shape.text.strip())
            word_path = tempfile.mktemp(suffix=".docx")
            doc.save(word_path)
            with open(word_path, "rb") as f:
                st.download_button("📄 Download Word File", f, file_name="converted.docx")
        except Exception as e:
            st.error(f"❌ Word export failed: {e}")

# === 6. YouTube Downloader (4K + audio fix) ===
elif tool == "📽️ YouTube Downloader":
    st.subheader("Download YouTube Video/Audio")
    url = st.text_input("Enter YouTube URL")
    format_option = st.selectbox("Choose format", ["🔊 MP3", "🎧 WAV", "📹 MP4 720p", "📹 MP4 1080p", "📹 MP4 4K"])
    if st.button("Download"):
        with tempfile.TemporaryDirectory() as tmpdir:
            outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")
            ydl_opts = {
                "outtmpl": outtmpl,
                "merge_output_format": "mp4",
                "postprocessor_args": ["-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "aac", "-b:a", "192k"],
                "prefer_ffmpeg": True
            }

            if "MP3" in format_option:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
            elif "WAV" in format_option:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]
            else:
                if "720p" in format_option:
                    ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best"
                elif "1080p" in format_option:
                    ydl_opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best"
                elif "4K" in format_option:
                    ydl_opts["format"] = "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    final_path = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp4"
                    st.success(f"✅ Downloaded: {info['title']}")
                    with open(final_path, "rb") as f:
                        st.download_button("📥 Download File", f, file_name=os.path.basename(final_path))
            except Exception as e:
                st.error(f"❌ Failed to download: {e}")

# === 7. Instagram Downloader (public reels/posts only) ===
elif tool == "📥 Instagram Downloader (Public Only)":
    st.subheader("Download public Instagram Reels or posts")
    ig_url = st.text_input("Paste Instagram URL")
    if st.button("Download"):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                    "quiet": True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(ig_url, download=True)
                    downloaded_path = ydl.prepare_filename(info)
                    with open(downloaded_path, "rb") as f:
                        st.download_button("📥 Download Media", f, file_name=os.path.basename(downloaded_path))
        except Exception as e:
            st.error(f"❌ Error: {e}")
