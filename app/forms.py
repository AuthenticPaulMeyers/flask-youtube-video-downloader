from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class URLForm(FlaskForm):
    link = StringField("URL", validators=[DataRequired()], render_kw={"placeholder": "Paste video URL here..."})
