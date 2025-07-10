from flask import render_template, redirect, url_for, Blueprint, request
from .forms import URLForm
from app.utils.functions import audio_downloader, video_downloader, get_url_info

download_bp = Blueprint('downloader', __name__, url_prefix='/downloader')

@download_bp.route('/', methods=['GET', 'POST'])
def index():
    
    form = URLForm()

    url = form.link.data

    if  form.validate_on_submit() or request.method == 'POST':
        # print("video link", url)
        # print(get_url_info(url))
        # return redirect(url_for('downloader.index'))

        # download audio
        quality = '720'

        video_downloader(url, quality)

    return render_template('index.html', form=form)









