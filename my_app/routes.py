from flask import render_template, redirect, url_for, Blueprint, request
from .forms import URLForm
from my_app.utils.functions import audio_downloader, video_downloader, get_url_info
from . import socketio

download_bp = Blueprint('downloader', __name__, url_prefix='/downloader')

@download_bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()

    if form.validate_on_submit():
        url = form.link.data.strip()
        if not url:
            return redirect(url_for('downloader.index'))

        info = get_url_info(url)

        return render_template('index.html', form=form, info=info)
    return render_template('index.html', form=form)

@socketio.on('download_request')
def handle_download_request(data):
    url = data['url']

    print(data)
    print('Received request from URL: ', url)
    if not url:
        return redirect(url_for('downloader.index'))
    # Run the download process in a separate thread to prevent blocking
    quality = data['quality']
    if not quality:
        return redirect(url_for('downloader.index'))
    print(quality)

    video_downloader(url, quality, socketio)
    # # Download video
    # if action == "download-video":
    #     video_downloader(url, quality, socketio)
        
    # # Download audio
    # if action == "download-audio":
    #    audio_downloader(url, socketio)










