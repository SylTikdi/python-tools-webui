
import streamlit as st
import os
import re
import platform
from PIL import Image
from docx import Document
from pptx import Presentation
import tempfile
import yt_dlp
import whisper
from pdf2image import convert_from_path

st.set_page_config(page_title="Python Tools Web UI", layout="wide")
st.title("🧰 Python Tools Web UI")

tool = st.sidebar.selectbox("Choose a tool", [
    "🎙️ Whisper Transcribe & Translate",
    "📄 PDF to JPEG",
    "🔄 Flip JPG Images",
    "📸 Combine JPG to PDF",
    "📗 PPTX to Word (Text + Images)",
    "📽️ YouTube Downloader"
])

# === Whisper AI ===
if tool == "🎙️ Whisper Transcribe & Translate":
    st.subheader("Upload audio/video to transcribe/translate")
    audio_file = st.file_uploader("Upload .mp3/.wav/.mp4", type=["mp3", "wav", "mp4"])
    source_lang = st.selectbox("Source language", ["auto", "english", "hindi", "marathi", "japanese"])
    target_lang = st.selectbox("Target language", ["english", "hindi", "marathi", "japanese"])
    output_format = st.radio("Output format", ["txt", "srt"])

    def transcribe_and_translate(file, source_lang, target_lang, output_format):
        model = whisper.load_model("base")
        file_path = os.path.join(tempfile.gettempdir(), file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())

        options = {
            "language": source_lang if source_lang != "auto" else None,
            "task": "translate" if source_lang != target_lang else "transcribe"
        }

        result = model.transcribe(file_path, **options)
        text = result["text"]
        segments = result.get("segments", [])

        if output_format == "txt":
            return text, "txt"
        elif output_format == "srt":
            srt_content = ""
            for i, segment in enumerate(segments, start=1):
                start = segment["start"]
                end = segment["end"]
                content = segment["text"].strip()

                def format_time(seconds):
                    h = int(seconds // 3600)
                    m = int((seconds % 3600) // 60)
                    s = int(seconds % 60)
                    ms = int((seconds - int(seconds)) * 1000)
                    return f"{h:02}:{m:02}:{s:02},{ms:03}"

                srt_content += f"{i}\n{format_time(start)} --> {format_time(end)}\n{content}\n\n"
            return srt_content, "srt"
        return "", "txt"

    if st.button("Transcribe & Translate") and audio_file:
        with st.spinner("Processing..."):
            try:
                result_text, ext = transcribe_and_translate(audio_file, source_lang, target_lang, output_format)
                st.success("✅ Done!")
                st.text_area("📄 Preview", result_text[:500] + "..." if len(result_text) > 500 else result_text, height=300)
                st.download_button("📥 Download", result_text, file_name=f"output.{ext}", mime="text/plain")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# === PDF to JPEG ===
elif tool == "📄 PDF to JPEG":
    st.subheader("Convert PDF pages to JPEG images")
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if pdf_file and st.button("Convert to JPEG"):
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, pdf_file.name)
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())
            try:
                images = convert_from_path(pdf_path)
                for i, img in enumerate(images):
                    img_path = os.path.join(tmpdir, f"page_{i+1}.jpg")
                    img.save(img_path, "JPEG")
                    st.image(img, caption=f"Page {i+1}")
                    with open(img_path, "rb") as file:
                        st.download_button(f"Download Page {i+1}", file, file_name=f"page_{i+1}.jpg")
                st.success("✅ Conversion complete.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# === Flip Images ===
elif tool == "🔄 Flip JPG Images":
    st.subheader("Flip Images Horizontally")
    uploaded = st.file_uploader("Upload images", type=["jpg", "jpeg"], accept_multiple_files=True)
    if uploaded:
        for img in uploaded:
            with Image.open(img) as im:
                flipped = im.transpose(Image.FLIP_LEFT_RIGHT)
                st.image(flipped, caption=f"Flipped - {img.name}")
                buf = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                flipped.save(buf.name)
                st.download_button("Download", data=open(buf.name, "rb"), file_name=img.name, mime="image/jpeg")

# === Combine to PDF ===
elif tool == "📸 Combine JPG to PDF":
    st.subheader("Combine Images to PDF")
    images = st.file_uploader("Upload JPG images", type=["jpg", "jpeg"], accept_multiple_files=True)
    if images and st.button("Create PDF"):
        def natural_sort_key(s):
            return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s.name)]
        images_sorted = sorted(images, key=natural_sort_key)

        pil_images = []
        for img in images_sorted:
            image = Image.open(img)
            if image.mode != "RGB":
                image = image.convert("RGB")
            pil_images.append(image)

        output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pil_images[0].save(output_pdf.name, save_all=True, append_images=pil_images[1:])
        st.success("✅ PDF created!")
        st.download_button("Download PDF", data=open(output_pdf.name, "rb"), file_name="output.pdf", mime="application/pdf")

# === PPTX to Word ===
elif tool == "📗 PPTX to Word (Text + Images)":
    st.subheader("Convert PPTX to Word Document")
    pptx_file = st.file_uploader("Upload .pptx file", type=["pptx"])
    if pptx_file and st.button("Convert"):
        with tempfile.TemporaryDirectory() as tmpdir:
            pptx_path = os.path.join(tmpdir, pptx_file.name)
            with open(pptx_path, "wb") as f:
                f.write(pptx_file.read())

            prs = Presentation(pptx_path)
            doc = Document()
            for slide in prs.slides:
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        text = shape.text.strip()
                        if text:
                            doc.add_paragraph(text)
            word_path = os.path.join(tmpdir, "output.docx")
            doc.save(word_path)
            st.success("✅ Converted to Word")
            st.download_button("Download Word", data=open(word_path, "rb"), file_name="converted.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# === YouTube Downloader ===
elif tool == "📽️ YouTube Downloader":
    st.subheader("Download YouTube Video/Audio")
    url = st.text_input("Enter YouTube URL")
    format_option = st.selectbox("Choose format", [
        "🔊 MP3 (audio)", 
        "🎧 WAV (audio)", 
        "📹 MP4 (video 720p)", 
        "📹 MP4 (video 1080p)", 
        "📹 MP4 (video 4K)"
    ])

    if st.button("Download"):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            # Base yt-dlp config
            ydl_opts = {
                "outtmpl": output_template,
                "merge_output_format": "mp4",
                "postprocessors": [],
                "postprocessor_args": [
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast",  # re-encode for compatibility
                    "-c:a", "aac", "-b:a", "192k"                         # ensure audio is encoded in AAC
                ],
                "prefer_ffmpeg": True,
                "ffmpeg_location": "ffmpeg"  # assumes ffmpeg is installed and on path
            }

            if "MP3" in format_option:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                })
            elif "WAV" in format_option:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav"
                })
            else:
                if "720p" in format_option:
                    ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best"
                elif "1080p" in format_option:
                    ydl_opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best"
                elif "4K" in format_option:
                    ydl_opts["format"] = "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best"

                # ensure proper audio/video muxing with AAC for Premiere compatibility
                ydl_opts["postprocessors"].append({
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    if not filename.endswith(".mp4") and "MP4" in format_option:
                        filename = os.path.splitext(filename)[0] + ".mp4"
                    st.success(f"✅ Downloaded: {info['title']}")
                    st.download_button("Download File", data=open(filename, "rb"), file_name=os.path.basename(filename))
            except Exception as e:
                st.error(f"❌ Failed to download: {e}")