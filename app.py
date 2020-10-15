from __future__ import division, print_function
from flask import Flask
import sys
import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, session, jsonify
from werkzeug.utils import secure_filename
import uuid 
from flask_session import Session
import datetime
import sqlite3
from PIL import Image
import io
from flask import send_file



UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = '--------------------SK-------------------'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Define a URL de inicialização do aplicativo com a criação de um Id único para cada sessão (session['id'])
#que tem por objetivo a identificação dos parâmetros submetidos pelo usuário para posterior processamento
@app.route('/')
def upload_form():
    session['id'] = str(uuid.uuid4())
    output_filename = str(session['id']) + "-output.jpg"
    is_processed =  {'var1':'processed', 'var2':'conundrum'}
    output = {'output_filename': output_filename, 'test': 'test'}
    reuploaded = {'reuploaded': 'false'}
    return render_template('index.html', is_processed=is_processed, output_filename=output_filename, output = output, reuploaded = reuploaded)

#Define a função que salva a imagem submetida pelo usuário na pasta uploads
#Importante notar que o nome dado à imagem após a submissão contém o Id da sessão (session['id'])
#e que caso o usuário mude de ideia e queira fazer o upload de outra imagem a imagem original é sobreescrita.
#Já que o método utiliza a função os.scandir() é importante a presença de pelo menos um arquivo na pasta uploads
@app.route('/', methods = ['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = session['id'] + "-" + secure_filename(file.filename)
        image = file.read()
        im = Image.open(io.BytesIO(image))
        im.thumbnail((500,427))
        for each in os.scandir(UPLOAD_FOLDER):
            if each.name[0:16] == filename[0:16]:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], each.name))
                try:
                	os.remove('static/stylized_images/' + session['id'] + '-output.jpg')
                except:
                	pass
                im.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                reuploaded = {'reuploaded': 'true'}
            else: 
                im.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Image successfully uploaded and displayed')
        output_filename = str(session['id']) + "-output.jpg"
        is_processed =  {'var1':'not_processed_yet', 'var2':'uploaded'}
        output = {'output_filename': output_filename, 'test': 'test'}
        reuploaded = {'reuploaded': 'false'}
        return render_template('index.html', filename=filename, output_filename = output_filename, is_processed=is_processed, output=output, reuploaded=reuploaded)
    else:
        flash('Allowed image types are -> png, jpg, jpeg')
    return redirect(request.url, is_processed=is_processed, code=301)

#Define a submissão dos parâmetros para o script neural_style.py (imagem submetida pelo usuário e estilo escolhido)
#sendo que o estilo é determinado através do formulário "model" e a identificação deste último parâmetro com a imagem
#submetida é mais uma vez determinada pelo Id da sessão (session['id'])
@app.route('/model', methods=['POST'])
def model_name():
    model = request.form['model']
    model = session['id'] + "-" + model
    for each in os.scandir(UPLOAD_FOLDER):
        if str(each.name)[0:16] == str(model)[0:16]:
            temp_dict = {'filename':each.name, 'model':model, 'time': datetime.datetime.now()}
            os.system("python3 neural_style/neural_style.py eval --content-image " + "static/uploads/" + str(temp_dict['filename']) +  " --model " +  "saved_models/" + str(temp_dict['model'][-6:]) + ".pth" + " --output-image " + "static/stylized_images/" + str(session['id']) + "-output.jpg" + " --cuda 0")
            is_processed =  {'var1':'not_processed_yet', 'var2':'processed'}
            output_filename = str(session['id']) + "-output.jpg"
            output = {'output_filename': output_filename, 'test': 'test'}
            reuploaded = {'reuploaded': 'false'}
        else:
            print('Counting other files')
    return render_template('index.html', is_processed=is_processed, output_filename=output_filename, output = output, reuploaded=reuploaded)

#Define a função que mostra ao usuário a imagem que foi por ele submetida à aplicação
@app.route('/display/<filename>')
def display_image(filename):
	output_filename = str(session['id']) + "-output.jpg"
	if '-output.jpg' not in filename:
		return redirect(url_for('static', filename='uploads/' + filename), code=301)
	else:
		return redirect(url_for('static', filename= 'stylized_images/' + output_filename), code=301)
	upload_form()


if __name__ == "__main__":
    app.run(threaded=True)
