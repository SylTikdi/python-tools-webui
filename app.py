
import streamlit as st
import os
import re
import tempfile
from PIL import Image
from docx import Document
from pptx import Presentation
from yt_dlp import YoutubeDL
from pdf2image import convert_from_path

# ========== TOOL 1: YouTube Downloader with full H.264 FFmpeg re-encode ==========
def youtube_download(url, format_choice, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }

    if format_choice == 'Audio (MP3)':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif format_choice == 'Audio (WAV)':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
        })
    else:
        resolution = format_choice.replace('p', '')
        ydl_opts.update({
            'format': f'bestvideo[ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4][height<={resolution}]',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'postprocessor_args': ['-c:v', 'libx264', '-crf', '23', '-preset', 'veryfast']
        })

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return True, info.get('title', 'Downloaded')

# ========== TOOL 2: PDF to JPEG ==========
def convert_pdf_to_jpg(uploaded_pdf, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_pdf.read())
        tmp_file_path = tmp_file.name

    images = convert_from_path(tmp_file_path)
    image_paths = []
    for i, img in enumerate(images):
        output_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        img.save(output_path, 'JPEG')
        image_paths.append(output_path)
    return image_paths

# ========== TOOL 3: Flip Images ==========
def flip_images(input_images, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_files = []
    for uploaded_file in input_images:
        img = Image.open(uploaded_file)
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        out_path = os.path.join(output_dir, uploaded_file.name)
        flipped.save(out_path, format='JPEG')
        output_files.append(out_path)
    return output_files

# ========== TOOL 4: Combine JPG to PDF ==========
def combine_images_to_pdf(input_images, output_path):
    sorted_imgs = sorted(input_images, key=lambda x: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', x.name)])
    image_list = []
    for uploaded_file in sorted_imgs:
        img = Image.open(uploaded_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        image_list.append(img)

    if image_list:
        first_image = image_list.pop(0)
        first_image.save(output_path, save_all=True, append_images=image_list)
        return output_path
    return None

# ========== TOOL 5: PPTX to Word ==========
def ppt_to_word(pptx_file, output_path):
    prs = Presentation(pptx_file)
    doc = Document()

    for i, slide in enumerate(prs.slides):
        doc.add_heading(f"Slide {i+1}", level=1)
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                doc.add_paragraph(shape.text.strip())

    doc.save(output_path)
    return output_path

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Python Tools WebUI", layout="centered")
st.title("🧰 Python Tools Web UI")

tool = st.sidebar.selectbox("Choose a tool", [
    "📽️ YouTube Downloader",
    "🖼️ Convert PDF to JPEG",
    "🔄 Flip JPG Images",
    "📸 Combine JPGs to PDF",
    "📤 PPTX to Word"
])

if tool == "📽️ YouTube Downloader":
    st.subheader("Download YouTube Videos or Audio")
    url = st.text_input("Paste YouTube URL")
    fmt = st.selectbox("Choose format", ["360p", "480p", "720p", "1080p", "4K", "Audio (MP3)", "Audio (WAV)"])
    if st.button("Download") and url:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                success, title = youtube_download(url, fmt, tmpdir)
                if success:
                    for file in os.listdir(tmpdir):
                        with open(os.path.join(tmpdir, file), "rb") as f:
                            st.download_button(f"Download: {file}", f, file_name=file)
                else:
                    st.error("❌ Failed to download.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

elif tool == "🖼️ Convert PDF to JPEG":
    st.subheader("Upload a PDF to Convert into JPEG Images")
    pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if st.button("Convert to JPEG") and pdf:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                image_paths = convert_pdf_to_jpg(pdf, tmpdir)
                for path in image_paths:
                    with open(path, "rb") as f:
                        st.image(f, use_column_width=True)
                        st.download_button(f"Download: {os.path.basename(path)}", f, file_name=os.path.basename(path))
            except Exception as e:
                st.error(f"❌ Failed to convert: {e}")

elif tool == "🔄 Flip JPG Images":
    st.subheader("Upload JPG Images to Flip Horizontally")
    images = st.file_uploader("Upload JPG images", type=["jpg", "jpeg"], accept_multiple_files=True)
    if st.button("Flip Images") and images:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_files = flip_images(images, tmpdir)
            for path in out_files:
                with open(path, "rb") as f:
                    st.image(f)
                    st.download_button(f"Download: {os.path.basename(path)}", f, file_name=os.path.basename(path))

elif tool == "📸 Combine JPGs to PDF":
    st.subheader("Upload JPGs to Combine into a PDF (sorted by filename)")
    imgs = st.file_uploader("Upload JPG images", type=["jpg", "jpeg"], accept_multiple_files=True)
    if st.button("Combine to PDF") and imgs:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_pdf = os.path.join(tmpdir, "combined.pdf")
            result = combine_images_to_pdf(imgs, out_pdf)
            if result:
                with open(result, "rb") as f:
                    st.download_button("Download Combined PDF", f, file_name="combined_output.pdf")
            else:
                st.error("❌ No valid images found.")

elif tool == "📤 PPTX to Word":
    st.subheader("Upload a PowerPoint (.pptx) to Extract Text into Word")
    pptx_file = st.file_uploader("Upload PPTX", type=["pptx"])
    if st.button("Convert to Word") and pptx_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "presentation.docx")
            try:
                result = ppt_to_word(pptx_file, output_path)
                with open(result, "rb") as f:
                    st.download_button("Download Word Doc", f, file_name="converted_ppt_to_word.docx")
            except Exception as e:
                st.error(f"❌ Word export failed: {e}")
