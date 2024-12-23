import os
import subprocess
from flask import Flask, render_template, request, send_file, url_for
import zipfile
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
FINAL_OUTPUT_FOLDER = 'finaloutput'
OUTPUT_FOLDER = 'output'
IMAGES_FOLDER = 'images'
INPUT_FOLDER = 'input'
ZIP_FILE_PATH = '/home/greenbaum-gpu/Reuben/CellDetection/output.zip'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FINAL_OUTPUT_FOLDER'] = FINAL_OUTPUT_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER
app.config['INPUT_FOLDER'] = INPUT_FOLDER

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FINAL_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(INPUT_FOLDER, exist_ok=True)

# Function to clear only files inside a folder, keeping the folder and subdirectories
def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)  # Remove only files
        elif os.path.isdir(file_path):
            clear_folder(file_path)  # Recursively clear subdirectories

# Function to copy the detections.png image to the static folder
def copy_detection_image():
    detection_image_path = os.path.join(app.config['FINAL_OUTPUT_FOLDER'], 'detections.png')
    static_image_path = os.path.join(app.static_folder, 'detections.png')
    
    if os.path.exists(detection_image_path):
        shutil.copy(detection_image_path, static_image_path)
        return 'detections.png'  # Return the filename for use in the template
    return None

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/process1', methods=['GET', 'POST'])
def process1():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Run the scripts
            subprocess.run(['python3', 'scripts/normalize.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/splitimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/detection.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/mergeimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/readingcsv.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])

            # Create the ZIP file
            with zipfile.ZipFile(ZIP_FILE_PATH, 'w') as zf:
                for root, _, files in os.walk(app.config['FINAL_OUTPUT_FOLDER']):
                    for f in files:
                        zf.write(os.path.join(root, f), arcname=f)

            # Copy the detections image for display
            image_filename = copy_detection_image()

            # Clear folders after processing
            clear_folder(UPLOAD_FOLDER)
            clear_folder(FINAL_OUTPUT_FOLDER)
            clear_folder(OUTPUT_FOLDER)
            clear_folder(IMAGES_FOLDER)
            clear_folder(INPUT_FOLDER)

            return render_template('download.html', download_link='/download1', image_filename=image_filename)
    return render_template('index1.html')

@app.route('/process2', methods=['GET', 'POST'])
def process2():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Run the scripts
            subprocess.run(['python3', 'scripts/normalize.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/splitimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/detection_SGN.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/mergeimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/readingcsv.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])

            # Create the ZIP file
            with zipfile.ZipFile(ZIP_FILE_PATH, 'w') as zf:
                for root, _, files in os.walk(app.config['FINAL_OUTPUT_FOLDER']):
                    for f in files:
                        zf.write(os.path.join(root, f), arcname=f)

            # Copy the detections image for display
            image_filename = copy_detection_image()

            # Clear folders after processing
            clear_folder(UPLOAD_FOLDER)
            clear_folder(FINAL_OUTPUT_FOLDER)
            clear_folder(OUTPUT_FOLDER)
            clear_folder(IMAGES_FOLDER)
            clear_folder(INPUT_FOLDER)

            return render_template('download.html', download_link='/download2', image_filename=image_filename)
    return render_template('index2.html')

@app.route('/download1')
def download1():
    return send_file(ZIP_FILE_PATH, as_attachment=True)

@app.route('/download2')
def download2():
    return send_file(ZIP_FILE_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
