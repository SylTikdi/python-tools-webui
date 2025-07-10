..
                    # Re-encode using ffmpeg for Premiere Pro compatibility
                    fixed_output = os.path.join(tmpdir, "fixed_output.mp4")
                    subprocess.run([
                        "ffmpeg", "-y", "-i", filename,
                        "-r", "30",
                        "-profile:v", "high",
                        "-level", "4.0",
                        "-pix_fmt", "yuv420p",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-c:a", "aac",
                        "-movflags", "+faststart",
                        fixed_output
                    ], check=True)
                    with open(fixed_output, "rb") as f:
                        st.download_button("⬇️ Download Final MP4", f.read(), file_name="fixed_video.mp4", mime="video/mp4")

.