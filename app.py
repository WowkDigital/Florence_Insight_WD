import os
import uuid
import sqlite3
import threading
import queue
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model_utils import FlorenceModel
from db import init_db, save_image_record, update_image_record, get_all_records

app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)

# Configuration settings
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize DB schema and pre-load the AI model into memory/GPU
init_db()
print("Starting initialize model...")
model = FlorenceModel()

# Queue and thread safety for sequential background processing on GPU
task_queue = queue.Queue()
process_lock = threading.Lock()

def process_worker():
    """Background worker that pulls tasks from the queue and processes them sequentially."""
    while True:
        task = task_queue.get()
        if task is None:
            break # Exit signal for the worker thread
            
        record_id, image_path, prompt, max_tokens, beams = task
        
        try:
            # Use a lock to ensure only one task accesses GPU resources at a time
            with process_lock:
                print(f"Background: Generating '{prompt}' for record ID {record_id}...")
                description = model.generate_caption(
                    image_path, 
                    task_prompt=prompt, 
                    max_new_tokens=max_tokens, 
                    num_beams=beams
                )
                # Persist result into database with completed status
                update_image_record(record_id, description, status='completed')
                print(f"Background: Task {record_id} successfully completed.")
        except Exception as e:
            # Log failure and update record with error details
            print(f"Background: Fatal error in task {record_id}: {str(e)}")
            update_image_record(record_id, f"Error: {str(e)}", status='error', error_msg=str(e))
        finally:
            task_queue.task_done()

# Start background worker thread immediately upon server startup
worker_thread = threading.Thread(target=process_worker, daemon=True)
worker_thread.start()

@app.route('/')
def home():
    """Serves the primary index.html file for the frontend application."""
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Accepts image uploads and enqueues them for background AI processing."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image block detected in request.'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected for upload.'}), 400
    
    # Retrieve and sanitize analysis parameters from the form
    prompt = request.form.get('prompt', '<DETAILED_CAPTION>')
    try:
        max_tokens = int(request.form.get('max_tokens', 1024))
        beams = int(request.form.get('beams', 3))
    except ValueError:
        return jsonify({'error': 'Analysis settings must contain valid integers.'}), 400

    # Persist the file on disk with a unique identifier
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{ext}"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(image_path)
    
    # Initialize a database record with a pending status for UI polling
    try:
        record_id = save_image_record(file.filename, "Analyzing...", unique_filename, status='pending')
        
        # Enqueue the background task for the worker thread
        task_queue.put((record_id, image_path, prompt, max_tokens, beams))
        
        return jsonify({
            'success': True,
            'record_id': record_id,
            'status': 'pending',
            'filename': file.filename,
            'image_url': f"/uploads/{unique_filename}"
        })
    except Exception as e:
        # Unexpected database or operational failure
        print(f"Critical error on enqueuing upload: {str(e)}")
        return jsonify({'error': f"Failed to enqueue analysis: {str(e)}"}), 500

@app.route('/images', methods=['GET'])
def list_images():
    """Returns a list of all images and their current analysis status from the DB."""
    try:
        records = get_all_records()
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': f"Failed to retrieve gallery records: {str(e)}"}), 500

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serves static image uploads for gallery viewing."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    # Launch Florence-Insight server locally on port 5000.
    # Note: reloader is disabled to prevent duplicate model initialization in memory.
    print("Florence-Insight live on: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)
