from app import flaskInst
from flask import render_template, url_for, redirect, request, session
from app.forms import UploadForm
# from werkzeug.datastructures import FileStorage
# from werkzeug.utils import secure_filename
import pandas as pd

@flaskInst.route('/', methods=['GET', 'POST'])
def fileupload():
    form = UploadForm()
    if form.validate_on_submit():
        myfile = form.file.data
        mydf = pd.read_csv(myfile)
        return mydf.to_html()
        
    return render_template('fileInput.html', form=form)
