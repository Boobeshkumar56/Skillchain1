import whisper
import requests
import json
import nltk
from nltk.tokenize import word_tokenize
import os
import subprocess
import torch
import tempfile

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except Exception: # Catching a general Exception instead of a specific NLTK one
    print("NLTK 'punkt' data not found, downloading...")
    nltk.download('punkt', quiet=True)

# Add specific download for punkt_tab - keeping this as it succeeded in the previous execution
try:
    nltk.data.find('tokenizers/punkt/PY3/english.pickle')
except Exception: # Catching a general Exception instead of a specific NLTK one
    print("NLTK 'punkt_tab' (english.pickle) data not found, downloading...")
    nltk.download('punkt', quiet=True) # Explicitly download punkt_tab


# ----------------------------
# Initialize NLTK and verify dependencies
# ----------------------------
# 1. Extract Audio from Video (New Step)
# ----------------------------
def extract_audio_from_video(video_path):
    """
    Extracts audio from a video file using FFmpeg.
    Returns the path to the temporary audio file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")

    # Create a temporary file path for the audio
    temp_audio_path = tempfile.mktemp(suffix=".mp3")

    print(f"Extracting audio from '{video_path}' to '{temp_audio_path}'...")
    command = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', temp_audio_path, '-y']
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Audio extraction successful.")
        return temp_audio_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        raise

# ----------------------------
# 2. Transcribe Audio with Whisper
# ----------------------------
def transcribe_audio(audio_path, model_size="base"):
    """Transcribes an audio file using OpenAI's Whisper model."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at {audio_path}")

    print(f"Transcribing audio using '{model_size}' model... This may take a while")
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    transcript = result.get("text", "")
    return transcript

# ----------------------------
# 3. Extract Keywords from Transcript
# ----------------------------
def extract_keywords(transcript, top_n=10):
    tokens = word_tokenize(transcript.lower())
    words = [t for t in tokens if t.isalpha()]
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    keywords = sorted(freq, key=freq.get, reverse=True)[:top_n]
    return keywords

# ----------------------------
# 4. Analyze Transcript with Gemini REST API
# ----------------------------
def analyze_with_gemini(transcript, metadata, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    prompt_text = f"""
Transcript:
{transcript}

Metadata:
Title: {metadata['title']}
Category: {metadata['category']}
Duration: {metadata['duration']} minutes
Difficulty (user input): {metadata['difficulty']}
Tags: {', '.join(metadata['tags'])}

Tasks:
1. Determine the difficulty level (Beginner, Intermediate, Advanced)
2. Suggest a complexity score (0-5)
3. Suggest additional tags/topics covered in the video
4. Generate a concise 1-2 line summary of the entire video content

Return the result in JSON format with keys:
"difficulty_level", "complexity_score", "additional_tags", "summary"
"""

    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": AIzaSyDzBsP9iA21qepnVd8PIdQad3CisrX0V-Q}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return {"error": f"Request failed: {response.status_code}", "details": response.text}

        result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Clean code blocks and extra whitespace
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[-1]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
        result_text = result_text.strip()

        result_json = json.loads(result_text)
    except Exception as e:
        result_json = {"error": f"Failed to parse JSON: {e}", "raw_text": response.text}

    return result_json

# ----------------------------
# 5. Main Pipeline
# ----------------------------
def main(video_path, metadata, gemini_api_key):
    temp_audio_path = None
    try:
        # Step 1: Extract Audio
        temp_audio_path = extract_audio_from_video(video_path)

        # Step 2: Transcribe (using a smaller model for speed)
        # Available models: "tiny", "base", "small", "medium", "large"
        # "tiny" is the fastest but least accurate, "large" is the slowest but most accurate.
        transcript = transcribe_audio(temp_audio_path, model_size="tiny")
        print("\n--- Transcript (first 1000 chars) ---\n")
        print(transcript[:1000])

        # Step 3: Extract keywords
        keywords = extract_keywords(transcript)
        print("\n--- Top Keywords ---\n", keywords)

        # Step 4: Analyze with Gemini
        analysis = analyze_with_gemini(transcript, metadata, gemini_api_key)
        print("\n--- Gemini Analysis ---\n")
        print(json.dumps(analysis, indent=2))

        # Step 5: Merge into enriched metadata
        enriched_metadata = metadata.copy()
        enriched_metadata.update({
            "difficulty_level": analysis.get("difficulty_level", metadata["difficulty"]),
            "complexity_score": analysis.get("complexity_score", None),
            "additional_tags": analysis.get("additional_tags", []),
            "summary": analysis.get("summary", ""),
            "keywords": keywords
        })

        print("\n--- Final Enriched Metadata ---\n")
        print(json.dumps(enriched_metadata, indent=2))

        return enriched_metadata
    finally:
        # Clean up the temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"\nCleaned up temporary file: {temp_audio_path}")

# ----------------------------
# 6. Module initialization
# ----------------------------
if __name__ == "__main__":
    print("This module is meant to be imported, not run directly.")