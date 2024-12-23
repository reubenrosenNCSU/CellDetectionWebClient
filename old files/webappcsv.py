import os
import time
import subprocess
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

# Define folders
UPLOAD_FOLDER = 'uploads'
IMAGE_FOLDER = 'image'
OUTPUT_FOLDER = 'output'

# Create Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set allowed file extensions
ALLOWED_EXTENSIONS = {'tiff', 'png', 'jpg', 'jpeg'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to clear files in a folder
def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Route to handle file upload and processing
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Simulate processing (can replace with actual processing logic)
            subprocess.run(['python3', 'splitimagev2.py', file_path])
            subprocess.run(['python3', 'appcsv.py', os.path.join(IMAGE_FOLDER, filename)])
            subprocess.run(['python3', 'mergeimage.py'])

            # Simulate time for processing
            time.sleep(3)

            # Return message indicating processing is complete
            return render_template('index.html', message='Processing complete. You can download the file now.', download_ready=True)
        
    return render_template('index.html', message=None, download_ready=False)

# Route to download the output folder as a ZIP
@app.route('/download')
def download_output():
    # Clear the folders before zipping and downloading
    clear_folder(UPLOAD_FOLDER)
    clear_folder(IMAGE_FOLDER)
    clear_folder(OUTPUT_FOLDER)

    # Placeholder for ZIP file logic
    output_zip = 'output.zip'
    # Implement zipping logic here

    return send_file(output_zip, as_attachment=True)

if __name__ == '__main__':
    # Make sure the folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
