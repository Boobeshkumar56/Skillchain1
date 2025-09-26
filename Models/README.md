# SkillChain AI Video Analysis Server

This is the backend server for the SkillChain video analysis system, which analyzes course videos, extracts information, and provides complexity scores and metadata.

## Features

- Video upload and processing via Flask API
- Background processing queue for resource-intensive tasks
- Audio extraction using FFmpeg
- Transcription with OpenAI's Whisper model
- Keyword extraction and natural language processing
- AI-powered analysis with Google's Gemini API
- Real-time status updates and results retrieval

## Requirements

- Python 3.8+
- NVIDIA GPU recommended for faster transcription (but not required)
- FFmpeg (required for audio extraction)

## Installation

1. Install FFmpeg (if not already installed):

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# MacOS with Homebrew
brew install ffmpeg
```

2. Install Python dependencies:

```bash
cd Models
pip install flask flask-cors openai-whisper torch nltk requests werkzeug
```

## Running the Server

From the Models directory:

```bash
python Main.py
```

This will start the Flask server on port 5000 by default.

## API Endpoints

### 1. Upload Video

- **URL**: `/api/video/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Parameters**:
  - `video`: The video file
  - `metadata`: JSON string containing:
    ```json
    {
      "title": "Video Title",
      "description": "Video Description",
      "category": "Category",
      "difficulty": "beginner|intermediate|advanced",
      "duration": 45, 
      "tags": ["tag1", "tag2"]
    }
    ```
- **Response**: JSON with job_id and status

### 2. Check Job Status

- **URL**: `/api/video/status/<job_id>`
- **Method**: `GET`
- **Response**: JSON with job status (queued, processing, completed, failed)

### 3. Get Job Results

- **URL**: `/api/video/result/<job_id>`
- **Method**: `GET`
- **Response**: JSON with analysis results including:
  - `difficulty_level`: Detected difficulty level
  - `complexity_score`: Numerical score from 1-10
  - `summary`: Brief content summary
  - `additional_tags`: AI-suggested tags
  - `keywords`: Extracted keywords
  - `aiAnalysis`: Object with complexity, suggestedTokens, and feedback

### 4. Special Endpoint for VideoUpload.tsx

- **URL**: `/api/educator/analyze-video/<video_id>`
- **Method**: `POST`
- **Response**: Compatibility endpoint for the frontend

## Testing the API

You can test the API with curl:

```bash
# Upload a video file with metadata
curl -X POST \
  http://localhost:5000/api/video/upload \
  -F "video=@/path/to/your/video.mp4" \
  -F 'metadata={"title":"Test Video","description":"Testing the API","category":"Programming Fundamentals","difficulty":"beginner","tags":["test","api"]}'

# Check job status
curl http://localhost:5000/api/video/status/<job_id>

# Get analysis results
curl http://localhost:5000/api/video/result/<job_id>
```

## Integration with VideoUpload.tsx

The VideoUpload.tsx component has been updated to connect to this Flask API. Key modifications include:

1. Added actual video file selection using expo-document-picker
2. Implemented form data preparation for multipart/form-data uploads
3. Added job status polling to check when processing is complete
4. Added result processing to update the UI with analysis data
5. Modified the UI to show real-time processing status

## Mobile Device Optimization

The server uses the following optimizations to work better on mobile devices:

1. Uses a smaller "tiny" Whisper model by default
2. Employs background processing for heavy tasks
3. Optimizes GPU usage when available
4. Truncates transcripts for faster analysis

## Troubleshooting

- **Video Processing Fails**: Check if FFmpeg is properly installed
- **Transcription Issues**: Try using a smaller model size in the `transcribe_audio` function
- **API Connection Errors**: Make sure the server is running and the URL in VideoUpload.tsx is correct
- **Memory Issues**: For large videos, you may need to increase the server's memory allocation
