
# ... [other imports and setup]

elif tool == "📽️ YouTube Downloader":
    st.subheader("📽️ Download YouTube Video or Audio")
    url = st.text_input("Enter YouTube URL")
    quality = st.selectbox("Select Format", ["MP3", "WAV", "720p MP4", "1080p MP4", "4K MP4"])

    if st.button("Download") and url:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {"outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s")}
                if quality in ["MP3", "WAV"]:
                    ydl_opts.update({
                        "format": "bestaudio",
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": quality.lower(),
                        }]
                    })
                else:
                    ydl_opts.update({
                        "format": "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/mp4",
                        "merge_output_format": "mp4",
                        "postprocessors": [{
                            "key": "FFmpegVideoConvertor",
                            "preferedformat": "mp4"
                        }]
                    })
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + (".mp3" if quality == "MP3" else ".wav" if quality == "WAV" else ".mp4")
                    with open(filename, "rb") as f:
                        st.download_button("Download", f.read(), file_name=os.path.basename(filename))
        except Exception as e:
            st.error(f"❌ Failed to download: {e}")
