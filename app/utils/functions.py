
# Required:
# Create a video downloader function wrap the download video functionalities.
# Pass arguements such as video quality and format.
# Create audio downloader function and pass the arguement such as audio format and size.
import yt_dlp
import os

# Get the path to the user's Downloads folder
home_dir = os.path.expanduser("~")

downloads_folder = os.path.join(home_dir, 'Downloads')

os.makedirs(downloads_folder, exist_ok=True) # Create the downloads folder if it doesnt exist

output_template = os.path.join(downloads_folder, '%(title)s.%(ext)s')

def get_url_info(url):
    file_options = {
        'noplaylist': True,
        'skip_download': True,
        'verbose': False,
    }

    try:
        with yt_dlp.YoutubeDL(file_options) as ydl:
            info_dict = ydl.extract_info(url, download=False)

        title = info_dict.get('title', 'N/A')
        thumbnail_url = info_dict.get('thumbnail', 'N/A')
        formats = info_dict.get('formats', [])

        for f in formats:
            ext = f.get('ext', 'N/A')
            resolution = f.get('resolution', 'N/A') # e.g., '1920x1080' or 'audio only'
            vcodec = f.get('vcodec', 'N/A')
            acodec = f.get('acodec', 'N/A')
            filesize_bytes = f.get('filesize') or f.get('filesize_approx') # Approximate size
            filesize_mb = "N/A"
            if filesize_bytes:
                filesize_mb = f"{filesize_bytes / (1024 * 1024):.2f} MB"

        return({
            'info':{
                'title': title,
                'thumbnail': thumbnail_url,
                'format': ext,
                'filesize_mb': filesize_mb
            }
        })
    
    except yt_dlp.utils.DownloadError as e:
        return({'error': f'An error occurred during download: {e}'})
    except Exception as e:
        return({'error': f'An unexpected error occurred: {e}'})

# A function to download videos
def video_downloader(url, quality):
    download_options = {
        'outtmpl': output_template,
        'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]',
    }

    with yt_dlp.YoutubeDL(download_options) as video:
        video.download([url])

    try:
        with yt_dlp.YoutubeDL(download_options) as audio:
            video.download([url])
        return({'message': 'Video downloaded successfully.'})
    except yt_dlp.utils.DownloadError as e:
        return({'error': f'An error occurred during download: {e}'})
    except Exception as e:
        return({'error': f'An unexpected error occurred: {e}'})
    
# A function to download audios
def audio_downloader(url):
    download_options = {
        'outtmpl': output_template,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(download_options) as audio:
            audio.download([url])
        return({'message': 'Audio downloaded successfully.'})
    except yt_dlp.utils.DownloadError as e:
        return({'error': f'An error occurred during download: {e}'})
    except Exception as e:
        return({'error': f'An unexpected error occurred: {e}'})