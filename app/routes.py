from flask import render_template, redirect, url_for, Blueprint, request
from .forms import URLForm
from app.utils.functions import audio_downloader, video_downloader, get_url_info

download_bp = Blueprint('downloader', __name__, url_prefix='/downloader')

@download_bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()

    if form.validate_on_submit():
        url = form.link.data.strip()
        if not url:
            return redirect(url_for('downloader.index'))

        info = get_url_info(url)
        
        quality = request.form.get('quality')

        action = request.form.get('action')

        # Download video
        if action == "download-video":
            if not quality:
                return redirect(url_for('downloader.index'))
            
            response = video_downloader(url, quality)
            print(response)
            
        # Download audio
        if action == "download-audio":
            response = audio_downloader(url)
            print(response)

        return render_template('index.html', form=form, info=info)
    return render_template('index.html', form=form)









