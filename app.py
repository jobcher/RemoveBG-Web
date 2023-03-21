import os
import uuid
import shutil
from rembg import remove, new_session
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

session = new_session()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    else:
        print('上传目录已存在')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return '没有文件上传', 400

    file = request.files['file']

    if file.filename == '':
        return '没有文件选择', 400

    if not allowed_file(file.filename):
        return '文件格式错误', 400

    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    return filename

@app.route('/process/<filename>')
def process(filename):
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output', filename)

    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    with open(input_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            input = i.read()
            output = remove(input, session=session)
            o.write(output)

    return filename

@app.route('/download/<filename>')
def download(filename):
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output', filename)

    if not os.path.exists(output_path):
        return 'File not found', 404

    return send_file(output_path, as_attachment=True)

@app.route('/progress/<filename>')
def progress(filename):
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output', filename)

    if not os.path.exists(input_path):
        return 'File not found', 404

    if os.path.exists(output_path):
        return '100'

    input_size = os.path.getsize(input_path)

    if input_size == 0:
        return '100'

    output_size = 0

    for root, dirs, files in os.walk(os.path.dirname(output_path)):
        for file in files:
            output_size += os.path.getsize(os.path.join(root, file))

    return str(int(output_size / input_size * 100))

@app.route('/clear')
def clear():
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
