from flask import Flask, request, jsonify
from flask_cors import CORS
import pyttsx3
import speech_recognition as sr
from autocorrect import Speller
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
spell = Speller()

# Text-to-Speech Endpoint
@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Text is required"}), 400

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id) 
    engine.save_to_file(text, 'output.mp3')
    engine.runAndWait()

    return jsonify({"message": "TTS completed", "file": "output.mp3"}), 200

# Speech-to-Text Endpoint
@app.route('/stt', methods=['POST'])
def stt():
    recognizer = sr.Recognizer()
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"error": "Audio file is required"}), 400

    audio_path = 'uploaded_audio.wav'
    audio_file.save(audio_path)

    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return jsonify({"text": text}), 200
        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand audio"}), 400
        except sr.RequestError as e:
            return jsonify({"error": f"Speech recognition error: {e}"}), 500
        finally:
            os.remove(audio_path)

# Spelling Correction Endpoint
@app.route('/spellcheck', methods=['POST'])
def spellcheck():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Text is required"}), 400

    corrected = spell(text)
    return jsonify({"corrected_text": corrected}), 200

# Run the Flask App
if __name__ == '__main__':
    app.run( port=5000)
