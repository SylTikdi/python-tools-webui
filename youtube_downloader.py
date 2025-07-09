import os
import yt_dlp

def get_video_info(url):
    """Fetch title, thumbnail, and available formats"""
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail', '')
            formats = info.get('formats', [])
            return title, thumbnail, formats
    except Exception as e:
        raise RuntimeError(f"Error fetching video info: {e}")

def download_youtube_video(url, output_dir, quality):
    os.makedirs(output_dir, exist_ok=True)
    outtmpl = os.path.join(output_dir, '%(title).80s.%(ext)s')

    # Audio-only
    if quality == "Audio only (MP3)":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'quiet': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # Format resolution to yt-dlp filters
        resolution_map = {
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "4K (2160p)": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
        }
        ydl_opts = {
            'format': resolution_map.get(quality, 'bestvideo+bestaudio/best'),
            'outtmpl': outtmpl,
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base_name = ydl.prepare_filename(info).rsplit('.', 1)[0]
        ext = ".mp3" if quality == "Audio only (MP3)" else ".mp4"
        return base_name + ext
