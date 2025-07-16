from flask import render_template, redirect, url_for, Blueprint, request
from .forms import URLForm
from app.utils.functions import audio_downloader, video_downloader, get_url_info

download_bp = Blueprint('downloader', __name__, url_prefix='/downloader')

QUALITY = ['1080', '720', '360']

@download_bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()

    url = form.link.data.strip()
    if not url:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        info = get_url_info(url)
        
        quality = request.form.get('quality')
        if quality not in QUALITY:
            return redirect(url_for('index'))

        action = request.form.get('action')
        if not action:
            return redirect(url_for('index'))
        
        if action == "download":
            response = video_downloader(url, quality)
            print(response)
        return render_template('index.html', form=form, info=info)
    return render_template('index.html', form=form)









