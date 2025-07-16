from flask import jsonify, Response, request
import os
import re
import subprocess
import yt_dlp
# Required:
# Create a video downloader function wrap the download video functionalities.
# Pass arguements such as video quality and format.
# Create audio downloader function and pass the arguement such as audio format.

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

        return {'video_title': title, 'thumbnail': thumbnail_url,
            }
    
    except yt_dlp.utils.DownloadError as e:
        return {'error': f'An error occurred during download: {e}'}, 400
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}, 400

# A function to download videos
def video_downloader(url, quality):
    download_options = {
        'outtmpl': output_template,
        'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]',
    }

    try:
        with yt_dlp.YoutubeDL(download_options) as video:
            video.download([url])
        return {'message': 'Video downloaded successfully.'}, 200
    
    except yt_dlp.utils.DownloadError as e:
        return {'error': f'An error occurred during download: {e}'}, 400
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}, 400
    
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
        return {'message': 'Audio downloaded successfully.'}, 200
    
    except yt_dlp.utils.DownloadError as e:
        return {'error': f'An error occurred during download: {e}'}, 400
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}, 400
    