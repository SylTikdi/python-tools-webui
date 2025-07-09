import streamlit as st
import os
from PIL import Image
import re
from pptx import Presentation
from docx import Document
from docx.shared import Inches
from yt_dlp import YoutubeDL
from pdf2image import convert_from_path
import tempfile
import requests

# --- Utilities ---

def flip_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            with Image.open(input_path) as img:
                flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
                flipped.save(output_path, format='JPEG')
    return True

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def images_to_pdf(input_folder, output_pdf):
    image_files = sorted([
        f for f in os.listdir(input_folder)
        if f.lower().endswith(('.jpg', '.jpeg'))
    ], key=natural_sort_key)

    if not image_files:
        return False, "No JPG images found."

    image_list = []
    for filename in image_files:
        path = os.path.join(input_folder, filename)
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        image_list.append(img)

    first_image = image_list.pop(0)
    first_image.save(output_pdf, save_all=True, append_images=image_list)
    return True, output_pdf

def pptx_to_word(pptx_path, docx_path):
    prs = Presentation(pptx_path)
    doc = Document()
    for i, slide in enumerate(prs.slides):
        doc.add_heading(f"Slide {i + 1}", level=1)
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text.strip()
                if text:
                    doc.add_paragraph(text)
        doc.add_page_break()
    doc.save(docx_path)
    return True

def youtube_download(url, format_choice, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
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
    else:
        resolution = format_choice.replace('p', '')
        ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return True, info.get('title', 'Downloaded')

def pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path)
    for i, img in enumerate(images):
        output_path = os.path.join(output_folder, f'slide{i+1}.jpg')
        img.save(output_path, 'JPEG')
    return True, output_folder

# --- Streamlit UI ---

st.set_page_config(page_title="Python Tools Web UI", layout="centered")
st.title("🧰 Python Tools Web UI (Cloud Edition)")

tool = st.sidebar.selectbox("Select a Tool", [
    "Flip JPG Images",
    "Combine Flipped JPGs to PDF",
    "Extract Text from PPTX to Word",
    "YouTube Downloader",
    "Convert PDF to JPEG"
])

if tool == "Flip JPG Images":
    st.header("🪞 Flip JPG Images Horizontally")
    uploaded = st.file_uploader("Upload JPG or JPEG files", type=["jpg", "jpeg"], accept_multiple_files=True)
    if uploaded:
        with tempfile.TemporaryDirectory() as in_dir, tempfile.TemporaryDirectory() as out_dir:
            for file in uploaded:
                file_path = os.path.join(in_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
            flip_images(in_dir, out_dir)
            st.success("Images flipped!")
            for file in os.listdir(out_dir):
                with open(os.path.join(out_dir, file), "rb") as f:
                    st.download_button("Download " + file, f, file_name=file)

elif tool == "Combine Flipped JPGs to PDF":
    st.header("📄 Combine JPGs into a PDF")
    uploaded = st.file_uploader("Upload Flipped JPGs", type=["jpg", "jpeg"], accept_multiple_files=True)
    if uploaded:
        with tempfile.TemporaryDirectory() as img_dir:
            for file in uploaded:
                with open(os.path.join(img_dir, file.name), "wb") as f:
                    f.write(file.read())
            output_pdf = os.path.join(img_dir, "output.pdf")
            success, msg = images_to_pdf(img_dir, output_pdf)
            if success:
                with open(output_pdf, "rb") as f:
                    st.download_button("Download PDF", f, file_name="output.pdf")
            else:
                st.error(msg)

elif tool == "Extract Text from PPTX to Word":
    st.header("📝 Convert PPTX to Word Document")
    pptx_file = st.file_uploader("Upload PPTX", type=["pptx"])
    if pptx_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            pptx_path = os.path.join(tmpdir, pptx_file.name)
            with open(pptx_path, "wb") as f:
                f.write(pptx_file.read())
            docx_path = os.path.join(tmpdir, "output.docx")
            try:
                pptx_to_word(pptx_path, docx_path)
                with open(docx_path, "rb") as f:
                    st.download_button("Download Word File", f, file_name="output.docx")
            except Exception as e:
                st.error(f"❌ Word export failed: {e}")

elif tool == "YouTube Downloader":
    st.header("🎬 YouTube Downloader")
    url = st.text_input("Paste YouTube URL")
    format_choice = st.selectbox("Choose format", ["360p", "480p", "720p", "1080p", "4K", "Audio (MP3)"])
    if st.button("Download") and url:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                success, title = youtube_download(url, format_choice, tmpdir)
                if success:
                    for file in os.listdir(tmpdir):
                        with open(os.path.join(tmpdir, file), "rb") as f:
                            st.download_button(f"Download: {file}", f, file_name=file)
                else:
                    st.error("❌ Failed to download.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

elif tool == "Convert PDF to JPEG":
    st.header("📽️ Convert PDF to JPEG")
    pdf_file = st.file_uploader("Upload exported Google Slides as PDF", type=["pdf"])
    if pdf_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "slides.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())
            out_folder = os.path.join(tmpdir, "jpgs")
            try:
                pdf_to_images(pdf_path, out_folder)
                st.success("Converted PDF to JPGs!")
                for img in sorted(os.listdir(out_folder)):
                    img_path = os.path.join(out_folder, img)
                    with open(img_path, "rb") as f:
                        st.image(img_path, width=250)
                        st.download_button(f"Download {img}", f, file_name=img)
            except Exception as e:
                st.error(f"❌ Failed to convert PDF to images: {e}")
