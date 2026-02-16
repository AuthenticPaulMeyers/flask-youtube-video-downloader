import os
import yt_dlp
import threading
from flask_socketio import emit
import re
import tempfile

# Required:
# Create a video downloader function wrap the download video functionalities.
# Pass arguements such as video quality and format.
# Create audio downloader function and pass the arguement such as audio format.

# Get the path to the user's Downloads folder
home_dir = os.path.expanduser("~")

downloads_folder = os.path.join(home_dir, 'Downloads', 'yt-downloads')

os.makedirs(downloads_folder, exist_ok=True) # Create the yt-downloads folder if it doesnt exist

# Create a temporary directory for yt-dlp to store cache and temporary files
import shutil
custom_temp_dir = tempfile.mkdtemp()

# Function to safely clear yt-dlp cache
def clear_ytdlp_cache():
    try:
        cache_dir = os.path.expanduser('~/.cache/yt-dlp')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
    except:
        pass

# Clear cache on startup
clear_ytdlp_cache()

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
        'js_runtime': 'node',  # Use Node.js for JavaScript execution
        'socket_timeout': 60,  # Increased timeout to reduce timeout errors
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
            'socket_timeout': 60,  # Increased timeout to 60 seconds
            'cachedir': custom_temp_dir,  # Use custom temporary directory
            'js_runtime': 'node',  # Use Node.js for JavaScript execution to extract signatures
            'retries': 5,  # Increase retries for failed downloads
            'fragment_retries': 5,  # Retry failed fragments
            'skip_unavailable_fragments': True,  # Skip fragments that fail after retries
            'overwrites': True,  # Overwrite existing files
            'quiet': False,  # Show output for debugging
            'no_warnings': False,  # Show warnings
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

        # Minimal options to avoid any postprocessing
        download_options = {
            'outtmpl': output_template,
            'format': 'worstaudio',
            'progress_hooks': [download_hook],
            'socket_timeout': 60,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            'overwrites': True,
            'quiet': False,
            'no_warnings': False,
            'no_post_overwrites': True,
            'keep_video': False,
        }

        try:
            with yt_dlp.YoutubeDL(download_options) as audio:
                info = audio.extract_info(url, download=False)
                if info:
                    # Download without any postprocessing
                    audio.download([url])
                    socketio.emit('progress', {
                        'status': 'finished',
                        'filename': info.get('title', 'Audio'),
                        'message': 'Audio downloaded successfully!'
                    })
        
        except yt_dlp.utils.DownloadError as e:
            socketio.emit('progress', {
                'status': 'error',
                'message': f"Download error: {str(e)}"
            })
        except Exception as e:
            socketio.emit('progress', {
                'status': 'error',
                'message': f"Error: {str(e)}"
            })
    
    thread = threading.Thread(target=download_thread)
    thread.start()