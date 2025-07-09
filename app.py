
import streamlit as st
import os
import tempfile
from yt_dlp import YoutubeDL

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
        ydl_opts['format'] = f'bestvideo[ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4][height<={resolution}]'

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return True, info.get('title', 'Downloaded')

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("🎬 YouTube Downloader")

url = st.text_input("Paste YouTube URL")
format_choice = st.selectbox("Choose format", ["360p", "480p", "720p", "1080p", "4K", "Audio (MP3)", "Audio (WAV)"])

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
