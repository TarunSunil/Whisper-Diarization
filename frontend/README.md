# Whisper Diarization Frontend

A modern, minimal web interface for the Whisper Diarization system with clean animations and intuitive user experience.

## Features

- **Drag & Drop Upload**: Easy audio file upload with drag and drop support
- **Real-time Processing**: Live progress updates during transcription
- **Speaker Diarization**: Automatic speaker identification and separation  
- **Multiple Formats**: Support for MP3, WAV, M4A, FLAC, and OGG files
- **Configurable Options**: Whisper model selection, language detection, and processing settings
- **Clean UI**: Modern, responsive design with smooth animations
- **Download Results**: Export transcripts as text files

## Technologies Used

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask with CORS support
- **AI Models**: OpenAI Whisper + NeMo Diarization
- **Styling**: Custom CSS with Inter font and gradient backgrounds

## Setup Instructions

### Prerequisites

- Python 3.8+ 
- NVIDIA GPU with CUDA (recommended for faster processing)
- Node.js (optional, for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TarunSunil/whisper-diarization.git
   cd whisper-diarization
   ```

2. **Install Python dependencies**
   ```bash
   # Install backend dependencies
   pip install -r backend/requirements.txt
   
   # Install whisper-diarization dependencies  
   pip install -r whisper-diarization/requirements.txt
   ```

3. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```

4. **Open the frontend**
   - Open your browser and navigate to `http://localhost:5000`
   - Or serve the frontend directory with any web server

### Usage

1. **Upload Audio**: Drag and drop an audio file or click to browse
2. **Configure Options**: 
   - Select Whisper model (larger = better quality, slower processing)
   - Choose language (auto-detect recommended)
   - Select processing device (GPU recommended)
   - Enable/disable source separation
3. **Process**: Click "Process Audio" to start transcription
4. **View Results**: Review the speaker-separated transcript
5. **Download**: Export the transcript as a text file

## API Endpoints

- `POST /api/upload` - Upload audio file and start processing
- `GET /api/status/<job_id>` - Get processing status and progress  
- `GET /api/result/<job_id>` - Get final transcript results
- `GET /api/download/<job_id>` - Download transcript file

## Configuration Options

### Whisper Models
- **large-v3**: Best quality, slowest processing
- **large-v2**: Recommended balance of quality and speed  
- **medium**: Good quality, faster processing
- **small**: Basic quality, fast processing
- **base**: Lowest quality, fastest processing

### Supported Languages
- Auto-detect (recommended)
- English, Spanish, French, German, Italian, Portuguese
- Russian, Japanese, Korean, Chinese
- Many more supported by Whisper

## System Requirements

### Minimum
- CPU: 4+ cores
- RAM: 8GB
- Storage: 10GB free space
- GPU: Optional (CPU processing available)

### Recommended  
- CPU: 8+ cores (modern Intel i7/AMD Ryzen 7)
- RAM: 16GB+ 
- Storage: SSD with 20GB+ free space
- GPU: NVIDIA RTX 3060 (8GB VRAM) or better

## Performance Notes

- **GPU Processing**: 10-20x faster than CPU
- **Model Size Impact**: Larger models need more VRAM and time
- **File Size**: Processing time scales with audio duration
- **Concurrent Users**: Each job requires significant resources

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── style.css           # Styling and animations  
├── script.js           # Frontend JavaScript logic
└── README.md           # This file

backend/
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies
├── uploads/            # Temporary upload storage
└── outputs/            # Generated transcript files

whisper-diarization/    # Core processing scripts
├── diarize.py          # Main diarization script  
├── helpers.py          # Utility functions
└── requirements.txt    # Processing dependencies
```

## Development

### Running in Development Mode

```bash
# Backend (with auto-reload)
cd backend  
export FLASK_ENV=development
python app.py

# Frontend (if using a dev server)
cd frontend
python -m http.server 8080
```

### Customization

- **Styling**: Modify `style.css` for theme changes
- **Layout**: Update `index.html` for structure changes  
- **Functionality**: Extend `script.js` for new features
- **Backend**: Customize `app.py` for API changes

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Use smaller Whisper model or CPU processing
2. **Slow Processing**: Ensure GPU drivers are installed and use GPU mode
3. **Upload Fails**: Check file size limits and supported formats
4. **Import Errors**: Install all dependencies with pip install -r requirements.txt

### Support

For issues and questions:
- Check the [whisper-diarization documentation](https://github.com/MahmoudAshraf97/whisper-diarization)
- Review system requirements and setup steps
- Ensure all dependencies are properly installed

## License

This project inherits licenses from its dependencies:
- Whisper: MIT License
- NeMo: Apache 2.0 License  
- Flask: BSD License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly  
5. Submit a pull request

---

Built with ❤️ using modern web technologies and state-of-the-art AI models.