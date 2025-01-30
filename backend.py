import os
import subprocess
from flask import Flask, render_template, request, session, redirect, url_for, send_file
import zipfile
import shutil

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
FINAL_OUTPUT_FOLDER = 'finaloutput'
ZIP_FILE_PATH = 'output.zip'
SNAPSHOT_FOLDER = 'snapshots'
OUTPUT_FOLDER = 'output'
INPUT_FOLDER = 'input'
IMAGES_FOLDER = 'images'
FTUPLOAD_FOLDER = 'fine_tune/ftupload'
CUSTOM_FOLDER='custom_output'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FINAL_OUTPUT_FOLDER'] = FINAL_OUTPUT_FOLDER
app.config['INPUT_FOLDER'] = INPUT_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER
app.config['FTUPLOAD_FOLDER'] = FTUPLOAD_FOLDER
app.config['CUSTOM_FOLDER'] = CUSTOM_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FINAL_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FTUPLOAD_FOLDER, exist_ok=True)

# Function to clear files inside a folder, keeping the folder structure intact
def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clear_folder(file_path)

# Function to copy detection image to static folder
def copy_detection_image():
    detection_image_path = os.path.join(app.config['FINAL_OUTPUT_FOLDER'], 'detections.png')
    static_image_path = os.path.join(app.static_folder, 'detections.png')
    
    if os.path.exists(detection_image_path):
        shutil.copy(detection_image_path, static_image_path)
        return 'detections.png'
    return None

# New function to copy the detection image to static folder
def copy_detection_to_static(image_filename):
    detection_image_path = os.path.join(app.config['CUSTOM_FOLDER'], image_filename)
    static_image_path = os.path.join(app.static_folder, 'images', image_filename)  # Ensure it's placed in static/images/
    
    if os.path.exists(detection_image_path):
        shutil.copy(detection_image_path, static_image_path)
        return f'images/{image_filename}'  # Return path relative to static folder
    return None

# Function to get the latest snapshot file
def get_latest_snapshot():
    snapshots = os.listdir(SNAPSHOT_FOLDER)
    snapshots = [f for f in snapshots if f.endswith('.h5')]  # Only H5 files
    if snapshots:
        latest_snapshot = max(snapshots, key=lambda f: os.path.getmtime(os.path.join(SNAPSHOT_FOLDER, f)))
        return latest_snapshot
    return None

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/process1', methods=['POST', 'GET'])
def process1():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            subprocess.run(['python3', 'scripts/normalize.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/splitimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/detection.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/mergeimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/mergecsv.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])

            with zipfile.ZipFile(ZIP_FILE_PATH, 'w') as zf:
                for root, _, files in os.walk(app.config['FINAL_OUTPUT_FOLDER']):
                    for f in files:
                        zf.write(os.path.join(root, f), arcname=f)

            image_filename = copy_detection_image()

            clear_folder(UPLOAD_FOLDER)
            clear_folder(INPUT_FOLDER)
            clear_folder(IMAGES_FOLDER)
            clear_folder(OUTPUT_FOLDER)
            clear_folder(FINAL_OUTPUT_FOLDER)

            session['process'] = 'process1'

            return render_template('download.html', download_link='/download', image_filename=image_filename)

    return render_template('index1.html')

@app.route('/process2', methods=['POST', 'GET'])
def process2():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            subprocess.run(['python3', 'scripts/normalize.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/splitimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/detection_SGN.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/mergeimage.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])
            subprocess.run(['python3', 'scripts/mergecsv.py', filepath, app.config['FINAL_OUTPUT_FOLDER']])

            with zipfile.ZipFile(ZIP_FILE_PATH, 'w') as zf:
                for root, _, files in os.walk(app.config['FINAL_OUTPUT_FOLDER']):
                    for f in files:
                        zf.write(os.path.join(root, f), arcname=f)

            image_filename = copy_detection_image()

            clear_folder(UPLOAD_FOLDER)
            clear_folder(INPUT_FOLDER)
            clear_folder(IMAGES_FOLDER)
            clear_folder(OUTPUT_FOLDER)
            clear_folder(FINAL_OUTPUT_FOLDER)

            session['process'] = 'process2'

            return render_template('download.html', download_link='/download', image_filename=image_filename)

    return render_template('index2.html')

@app.route('/fine_tuning', methods=['GET', 'POST'])
def fine_tuning():
    if request.method == 'POST':
        epochs = request.form['epochs']
        batch_size = request.form['batch_size']
        steps = request.form['steps']

        process = session.get('process')

        # Determine the classes_file based on the selected process
        if process == 'process1':
            classes_file = 'fine_tune/color.csv'
        elif process == 'process2':
            classes_file = 'fine_tune/monochrome.csv'

        # Upload CSV and image files for fine-tuning
        csv_file_uploaded = request.files['csv_file']
        image_files = request.files.getlist('image_files')

        if not csv_file_uploaded or not image_files:
            return "CSV file and image files are required", 400

        # Save the uploaded CSV file in the fine-tuning upload folder
        csv_file_path = os.path.join(app.config['FTUPLOAD_FOLDER'], csv_file_uploaded.filename)
        csv_file_uploaded.save(csv_file_path)

        # Save the image files
        image_paths = []
        for image in image_files:
            image_path = os.path.join(app.config['FTUPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            image_paths.append(image_path)

        # Run the fine-tuning script with the uploaded CSV file and images
        subprocess.run([
            'python3', 'keras_retinanet/bin/train.py',
            '--weights', 'snapshots/combine.h5',
            '--epochs', epochs,
            '--batch-size', batch_size,
            '--steps', steps,
            '--snapshot-path', 'snapshots/',
            'csv', csv_file_path, classes_file
        ])

        latest_snapshot = get_latest_snapshot()

        message = f"Fine-tuning started with {epochs} epochs, {batch_size} batch size, and {steps} step size."

        return render_template('fine_tuning_result.html', message=message, snapshot_filename=latest_snapshot)

    return render_template('fine_tuning.html')

@app.route('/fine_tuning_result')
def fine_tuning_result():
    snapshot_filename = request.args.get('snapshot_filename')
    if snapshot_filename:
        return send_file(os.path.join(SNAPSHOT_FOLDER, snapshot_filename), as_attachment=True)
    return render_template('fine_tuning_result.html')

@app.route('/download')
def download():
    return send_file(ZIP_FILE_PATH, as_attachment=True)

# New route for running detection with the latest fine-tuned weights
@app.route('/run_detection', methods=['POST', 'GET'])
def run_detection():
    if request.method == 'POST':
        # Get uploaded files (image and .h5 file)
        image = request.files['image']
        h5file = request.files['h5file']
        process = session.get('process')

        if image and h5file:
            # Save the uploaded files
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            h5file_path = os.path.join(app.config['UPLOAD_FOLDER'], h5file.filename)
            image.save(image_path)
            h5file.save(h5file_path)

            # Run the detection script with the uploaded .h5 file and image
            if process=='process2':
                subprocess.run(['python3', 'scripts/custom_detection.py', image_path, h5file_path, app.config['CUSTOM_FOLDER']])
            else:
                subprocess.run(['python3', 'scripts/custom_detection_color.py', image_path, h5file_path, app.config['CUSTOM_FOLDER']])
            # After running detection, check for the resulting image
            detection_image_path = os.path.join(app.config['CUSTOM_FOLDER'], 'custom_detection.png')  # This could vary
            if os.path.exists(detection_image_path):
                # Use the new function to copy the detection image to the static folder
                image_filename = copy_detection_to_static('custom_detection.png')  # Adjust file name if needed
                
                custom_zip_path = 'custom_output.zip'
                with zipfile.ZipFile(custom_zip_path, 'w') as zf:
                    for root, _, files in os.walk(app.config['CUSTOM_FOLDER']):
                        for f in files:
                            file_path = os.path.join(root, f)
                            # Preserve relative path inside ZIP
                            arcname = os.path.relpath(file_path, app.config['CUSTOM_FOLDER'])
                            zf.write(file_path, arcname=arcname)
                
                return render_template('detection_result.html', image_filename=image_filename, is_custom=True)
            else:
                return "Detection image not found. Please check your detection script.", 404
        else:
            return "Both the image and .h5 file are required.", 400
    return render_template('run_detection.html')

# New route for annotation
@app.route('/annotate')
def annotate():
    # Redirect to the Flask app running on port 5001
    return redirect("http://127.0.0.1:5001", code=302)

@app.route('/download_custom')
def download_custom():
    custom_zip_path = os.path.join(app.root_path, 'custom_output.zip')
    if os.path.exists(custom_zip_path):
        return send_file(
            custom_zip_path,
            as_attachment=True,
            download_name='custom_detection_results.zip'
        )
    return "ZIP file not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)
