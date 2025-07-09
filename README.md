# Python Tools Web UI

A simple web-based UI built with Streamlit that combines multiple tools:

## ✨ Features

- 🔄 Convert PowerPoint (.pptx) to JPEG images
- 🪞 Flip JPEGs horizontally
- 🧾 Combine flipped JPEGs into a single PDF
- 📝 Extract text and images from PPTX and export to Word (.docx)
- 🎬 Download YouTube videos or audio (MP3), with format selection up to 4K

## 🚀 How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the app:
   ```
   streamlit run app.py
   ```

## 📦 Requirements

- `streamlit`
- `Pillow`
- `python-docx`
- `python-pptx`
- `yt-dlp`
- `comtypes` (Windows-only, for PPT export via PowerPoint)

## 🔗 Deployment

Deploy free to [Streamlit Cloud](https://streamlit.io/cloud) and share with your team.
