import os
import yt_dlp
import threading
from flask_socketio import emit
import re
# Required:
# Create a video downloader function wrap the download video functionalities.
# Pass arguements such as video quality and format.
# Create audio downloader function and pass the arguement such as audio format.

# Get the path to the user's Downloads folder
home_dir = os.path.expanduser("~")

downloads_folder = os.path.join(home_dir, 'Downloads')

os.makedirs(downloads_folder, exist_ok=True) # Create the downloads folder if it doesnt exist

# A custom progress hook function
def my_hook(d):
    # This function is called by yt-dlp for each progress update
    status = d['status']
    
    if status == 'downloading':
        # Emit a 'progress' event to the frontend with download details
        percent = d.get('_percent', '0%')
        speed = d.get('_speed_str', 'N/A')
        
        # We also need the filename to identify the specific download
        filename = os.path.basename(d.get('filename', 'Unknown'))
        ansi_escape_pattern = re.compile(r'\x1b\[.*?m')
        cleaned_speed = ansi_escape_pattern.sub('', speed).strip()
        # 'emit' sends a message to the client over the socket
        emit('progress', {
            'status': 'downloading',
            'percent': f'{round(percent)}%',
            'speed': cleaned_speed,
            'filename': filename,
        })

    elif status == 'finished':
        filename = d.get('filename', 'Unknown')
        emit('progress', {
            'status': 'finished',
            'filename': os.path.basename(filename),
            'message': 'Download complete!'
        })
        print(f"Finished downloading: {filename}")
        return
        
    elif status == 'error':
        error_message = d.get('error', 'Unknown error')
        emit('progress', {
            'status': 'error',
            'message': f"Download failed: {error_message}"
        })
        print(f"Error during download: {error_message}")


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
def video_downloader(url, quality, socketio):

    def download_hook(d):
        status = d['status']
        if status == 'downloading':
            percent = d.get('_percent', '0%')
            speed = d.get('_speed_str', 'N/A')
            filename = os.path.basename(d.get('filename', 'Unknown'))

            ansi_escape_pattern = re.compile(r'\x1b\[.*?m')
            cleaned_speed = ansi_escape_pattern.sub('', speed).strip()
        
            socketio.emit('progress', {
                'status': 'downloading',
                'percent': f'{round(percent)}%',
                'speed': cleaned_speed,
                'filename': filename,
            })
        elif status == 'finished':
            filename = d.get('filename', 'Unknown')
            socketio.emit('progress', {
                'status': 'finished',
                'filename': os.path.basename(filename),
                'message': 'Download complete!'
            })
        elif status == 'error':
            error_message = d.get('error', 'Unknown error')
            socketio.emit('progress', {
                'status': 'error',
                'message': f"Download failed: {error_message}"
            })

    def download_thread():

        output_template = os.path.join(downloads_folder, '%(title)s.%(ext)s')

        download_options = {
            'outtmpl': output_template,
            'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]',
            'progress_hooks': [download_hook],
        }

        try:
            with yt_dlp.YoutubeDL(download_options) as video:
                video.download([url])

        except yt_dlp.utils.DownloadError as e:
          # Emit error through the socketio instance
            socketio.emit('progress', {
                'status': 'error',
                'message': f"An error occurred during download: {e}"
            }), 400
        except Exception as e:
            # Emit an error if something goes wrong with yt-dlp itself
            socketio.emit('progress', {
                'status': 'error',
                'message': f"An unexpected error occurred: {str(e)}"
            })
    
    # Start the thread to handle the download
    thread = threading.Thread(target=download_thread)
    thread.start()

# A function to download audios
def audio_downloader(url, socketio):

    def download_hook(d):
        status = d['status']
        if status == 'downloading':
            percent = d.get('_percent', '0%')
            speed = d.get('_speed_str', 'N/A')
            filename = os.path.basename(d.get('filename', 'Unknown'))

            ansi_escape_pattern = re.compile(r'\x1b\[.*?m')
            cleaned_speed = ansi_escape_pattern.sub('', speed).strip()
        
            socketio.emit('progress', {
                'status': 'downloading',
                'percent': f'{round(percent)}%',
                'speed': cleaned_speed,
                'filename': filename,
            })
        elif status == 'finished':
            filename = d.get('filename', 'Unknown')
            socketio.emit('progress', {
                'status': 'finished',
                'filename': os.path.basename(filename),
                'message': 'Download complete!'
            })
        elif status == 'error':
            error_message = d.get('error', 'Unknown error')
            socketio.emit('progress', {
                'status': 'error',
                'message': f"Download failed: {error_message}"
            })
    
    def download_thread():
        output_template = os.path.join(downloads_folder, '%(title)s.%(ext)s')

        download_options = {
            'outtmpl': output_template,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [download_hook],
        }

        try:
            with yt_dlp.YoutubeDL(download_options) as audio:
                audio.download([url])
        
        except yt_dlp.utils.DownloadError as e:
            socketio.emit('progress', {
                'status': 'error',
                'message': f"An unexpected error occurred: {str(e)}"
            }), 400
        except Exception as e:
            # Emit an error if something goes wrong with yt-dlp itself
            socketio.emit('progress', {
                'status': 'error',
                'message': f"An unexpected error occurred: {str(e)}"
            })
    # Start the thread to handle the download
    thread = threading.Thread(target=download_thread)
    thread.start()