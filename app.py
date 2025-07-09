import streamlit as st
import os
import shutil

from export_ppt_to_jpg import export_ppt_to_jpg
from flip_images import flip_images
from images_to_pdf_sorted import images_to_pdf
from ppt_to_word import ppt_to_word
from youtube_downloader import download_youtube_video, get_video_info

# === Folder Setup ===
ASSET_FOLDER = "assets"
JPEG_FOLDER = "output/JPEG"
FLIPPED_FOLDER = "output/Flipped"
PDF_PATH = "output/PDF_output/final_output.pdf"
WORD_PATH = "output/ppt_content.docx"
YT_DOWNLOAD_FOLDER = "output/yt_downloads"
EXTRACTED_IMG_FOLDER = os.path.join(ASSET_FOLDER, "extracted_images")

# === Streamlit Config ===
st.set_page_config(page_title="Python Tools Web UI", layout="centered")
st.title("🧰 Python Tools Web UI")

# === Sidebar: Tool Selection ===
tool = st.sidebar.radio("Choose a Tool", [
    "🔄 PPTX to JPEG",
    "🪞 Flip JPEGs Horizontally",
    "🧾 Combine JPEGs into PDF",
    "📝 PPTX to Word (Text + Images)",
    "🎬 YouTube Video Downloader"
])

# === Tool 1: PPTX to JPEG ===
if tool == "🔄 PPTX to JPEG":
    st.header("🔄 Convert PPTX to JPEG Slides")
    uploaded_file = st.file_uploader("Upload a .pptx file", type=["pptx"])

    if uploaded_file and st.button("Convert to JPEG"):
        os.makedirs(ASSET_FOLDER, exist_ok=True)
        os.makedirs(JPEG_FOLDER, exist_ok=True)

        pptx_path = os.path.join(ASSET_FOLDER, uploaded_file.name)
        with open(pptx_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            export_ppt_to_jpg(pptx_path, JPEG_FOLDER)
            st.success(f"✅ Slides saved as JPEGs in: {JPEG_FOLDER}")
        except Exception as e:
            st.error(f"❌ Failed: {e}")

# === Tool 2: Flip JPEGs ===
elif tool == "🪞 Flip JPEGs Horizontally":
    st.header("🪞 Flip JPEG Images Horizontally")

    if st.button("Flip Images"):
        try:
            os.makedirs(FLIPPED_FOLDER, exist_ok=True)
            flip_images(JPEG_FOLDER, FLIPPED_FOLDER)
            st.success(f"✅ Flipped images saved to: {FLIPPED_FOLDER}")
        except Exception as e:
            st.error(f"❌ Failed to flip images: {e}")

# === Tool 3: JPEG to PDF ===
elif tool == "🧾 Combine JPEGs into PDF":
    st.header("🧾 Combine Flipped JPEGs into a PDF")

    if st.button("Create PDF"):
        try:
            os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
            result = images_to_pdf(FLIPPED_FOLDER, PDF_PATH)
            if result:
                st.success("✅ PDF created!")
                with open(PDF_PATH, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name="slides_output.pdf")
            else:
                st.error("❌ No images found to convert.")
        except Exception as e:
            st.error(f"❌ PDF generation failed: {e}")

# === Tool 4: PPTX to Word ===
elif tool == "📝 PPTX to Word (Text + Images)":
    st.header("📝 Extract Text & Images from PPTX to Word")
    uploaded_file = st.file_uploader("Upload a .pptx file", type=["pptx"])

    if uploaded_file and st.button("Convert to Word"):
        os.makedirs(ASSET_FOLDER, exist_ok=True)
        os.makedirs(EXTRACTED_IMG_FOLDER, exist_ok=True)

        pptx_path = os.path.join(ASSET_FOLDER, uploaded_file.name)
        with open(pptx_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            ppt_to_word(pptx_path, WORD_PATH, EXTRACTED_IMG_FOLDER)
            st.success("✅ Word document created!")
            with open(WORD_PATH, "rb") as f:
                st.download_button("📥 Download Word Doc", f, file_name="ppt_content.docx")
        except Exception as e:
            st.error(f"❌ Word export failed: {e}")

# === Tool 5: YouTube Downloader with Format Picker ===
elif tool == "🎬 YouTube Video Downloader":
    st.header("🎬 YouTube Video Downloader")

    yt_url = st.text_input("Enter YouTube video URL:")

    if yt_url:
        try:
            title, thumbnail, formats = get_video_info(yt_url)
            st.markdown(f"**📺 Title:** {title}")
            if thumbnail:
                st.image(thumbnail, width=480)

            quality = st.selectbox("Choose Quality", [
                "Audio only (MP3)", "360p", "480p", "720p", "1080p", "4K (2160p)"
            ])

            if st.button("⬇️ Download"):
                os.makedirs(YT_DOWNLOAD_FOLDER, exist_ok=True)
                result_path = download_youtube_video(yt_url, YT_DOWNLOAD_FOLDER, quality)

                st.success("✅ Download complete!")
                with open(result_path, "rb") as f:
                    st.download_button("📥 Download File", f, file_name=os.path.basename(result_path))

        except Exception as e:
            st.error(f"❌ Failed: {e}")
