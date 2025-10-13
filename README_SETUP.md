# Whisper Diarization - Setup Guide

## 🎉 Alternative Setup (Windows Compatible)

This project now includes a **simplified diarization script** that works on Windows without requiring Visual C++ Build Tools!

## ✅ What's Installed

Successfully installed dependencies:
- ✅ **faster-whisper** - Fast Whisper transcription
- ✅ **torch** - PyTorch framework
- ✅ **pyannote.audio** - Speaker diarization (alternative to NeMo)
- ✅ **demucs** - Audio source separation
- ✅ **deepmultilingualpunctuation** - Automatic punctuation
- ✅ **nltk** - Natural language processing
- ✅ **Flask** - Web backend
- ✅ **flask-cors** - Cross-origin resource sharing

## 🚫 What's NOT Installed

- ❌ **ctc-forced-aligner** - Requires Microsoft Visual C++ 14.0 compiler
  - **Solution**: We created an alternative script (`diarize_simple.py`) that uses pyannote.audio instead

## 🚀 Quick Start

### 1. Test Your Setup
```bash
python test_setup.py
```

### 2. Start the Server
```bash
cd backend
python app.py
```

### 3. Open in Browser
Navigate to: `http://localhost:5000`

## 📝 Usage

### Upload Mode
1. Click "Upload Audio" tab
2. Drag & drop an audio file or click to browse
3. Select Whisper model (tiny/base/small/medium/large)
4. Click "Start Processing"
5. Wait for transcription to complete
6. Download results

### Microphone Mode
1. Click "Record Audio" tab
2. Click microphone button to start recording
3. Speak into your microphone
4. Click stop button when done
5. Process the recording

## 🔧 Configuration

### Whisper Models
- **tiny** - Fastest, least accurate (~1GB RAM)
- **base** - Fast, good for testing (~1GB RAM)
- **small** - Balanced (~2GB RAM)
- **medium** - Better accuracy (~5GB RAM)
- **large-v2/v3** - Best accuracy (~10GB RAM)

### Device Settings
- **CPU** - Works on all systems (slower)
- **CUDA** - Requires NVIDIA GPU (faster)

## 🎯 Alternative Scripts

### Original Script (Requires ctc-forced-aligner)
```bash
python whisper-diarization/diarize.py --audio-files audio.wav --whisper-model base
```

### Simplified Script (Windows Compatible)
```bash
python whisper-diarization/diarize_simple.py --audio-files audio.wav --whisper-model base
```

## 📦 Output Files

The system generates:
- **TXT** - Plain text transcript with speaker labels
- **SRT** - Subtitle file with timestamps
- **JSON** - Structured data for further processing

## 🔐 Hugging Face Token (Optional)

For better diarization with pyannote.audio:

1. Create account at: https://huggingface.co
2. Get token at: https://huggingface.co/settings/tokens
3. Accept terms at: https://huggingface.co/pyannote/speaker-diarization-3.1
4. Use with: `--hf-token YOUR_TOKEN`

Without token, system will default to single speaker mode.

## 🐛 Troubleshooting

### Issue: Slow Processing
**Solution**: Use smaller models (tiny/base) or enable GPU

### Issue: Out of Memory
**Solution**: Reduce model size or close other applications

### Issue: Diarization Not Working
**Solution**: Add Hugging Face token or use `--no-diarization` flag

### Issue: Audio Format Not Supported
**Solution**: Convert to WAV, MP3, M4A, FLAC, or OGG

## 📊 Performance

| Model  | Speed (CPU) | Speed (GPU) | Accuracy |
|--------|-------------|-------------|----------|
| tiny   | 1x realtime | 10x         | ⭐⭐     |
| base   | 0.5x        | 8x          | ⭐⭐⭐   |
| small  | 0.3x        | 6x          | ⭐⭐⭐⭐ |
| medium | 0.2x        | 4x          | ⭐⭐⭐⭐⭐|
| large  | 0.1x        | 2x          | ⭐⭐⭐⭐⭐|

## 🔗 References

- [Whisper by OpenAI](https://github.com/openai/whisper)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- [Pyannote Audio](https://github.com/pyannote/pyannote-audio)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 📄 License

This project combines multiple open-source components. Check individual licenses for each dependency.

## 🎊 Success!

Your Whisper Diarization system is ready! Enjoy transcribing! 🎤✨
