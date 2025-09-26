from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import tempfile
from Main import main as process_video
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Create a thread pool for handling video processing
executor = ThreadPoolExecutor(max_workers=3)  # Adjust max_workers based on your VM resources

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/video/upload', methods=['POST'])
def upload_video():
    try:
        # Check if video file is present in request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Check if metadata is present
        if 'metadata' not in request.form:
            return jsonify({'error': 'No metadata provided'}), 400

        try:
            metadata = request.form.get('metadata')
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid metadata JSON format'}), 400

        if not allowed_file(video_file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Save video file temporarily
        filename = secure_filename(video_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(temp_path)

        try:
            # Get the API key from environment variable
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if not gemini_api_key:
                return jsonify({'error': 'GEMINI_API_KEY environment variable not set'}), 500

            # Process the video in a separate thread
            future = executor.submit(process_video, temp_path, metadata, gemini_api_key)
            enriched_metadata = future.result()  # Wait for the processing to complete

            return jsonify({
                'status': 'success',
                'message': 'Video processed successfully',
                'data': enriched_metadata
            })

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return jsonify({'error': f'Error processing video: {str(e)}'}), 500

        finally:
            # Clean up the temporary video file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Add environment variable check
    if not os.environ.get('GEMINI_API_KEY'):
        logger.warning('GEMINI_API_KEY environment variable not set')
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port)
