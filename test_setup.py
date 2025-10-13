"""
Quick test script to verify all dependencies are working
"""
import sys

def test_imports():
    """Test that all required packages can be imported"""
    errors = []
    
    print("Testing dependencies...")
    print("=" * 60)
    
    # Test 1: faster-whisper
    try:
        import faster_whisper
        print("✓ faster-whisper imported successfully")
    except Exception as e:
        errors.append(f"✗ faster-whisper: {str(e)}")
        print(f"✗ faster-whisper: {str(e)}")
    
    # Test 2: torch
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"✓ torch imported successfully (device: {device})")
    except Exception as e:
        errors.append(f"✗ torch: {str(e)}")
        print(f"✗ torch: {str(e)}")
    
    # Test 3: pyannote.audio
    try:
        from pyannote.audio import Pipeline
        print("✓ pyannote.audio imported successfully")
    except Exception as e:
        errors.append(f"✗ pyannote.audio: {str(e)}")
        print(f"✗ pyannote.audio: {str(e)}")
    
    # Test 4: Flask
    try:
        import flask
        print("✓ Flask imported successfully")
    except Exception as e:
        errors.append(f"✗ Flask: {str(e)}")
        print(f"✗ Flask: {str(e)}")
    
    # Test 5: demucs
    try:
        import demucs
        print("✓ demucs imported successfully")
    except Exception as e:
        errors.append(f"✗ demucs: {str(e)}")
        print(f"✗ demucs: {str(e)}")
    
    # Test 6: deepmultilingualpunctuation
    try:
        from deepmultilingualpunctuation import PunctuationModel
        print("✓ deepmultilingualpunctuation imported successfully")
    except Exception as e:
        errors.append(f"✗ deepmultilingualpunctuation: {str(e)}")
        print(f"✗ deepmultilingualpunctuation: {str(e)}")
    
    # Test 7: nltk
    try:
        import nltk
        print(f"✓ nltk imported successfully")
    except Exception as e:
        errors.append(f"✗ nltk: {str(e)}")
        print(f"✗ nltk: {str(e)}")
    
    print("=" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} error(s) found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ All dependencies are working correctly!")
        return True

def test_whisper_model():
    """Test loading a small Whisper model"""
    try:
        print("\n" + "=" * 60)
        print("Testing Whisper model loading...")
        print("=" * 60)
        
        from faster_whisper import WhisperModel
        import torch
        
        device = "cpu"  # Use CPU for quick test
        model = WhisperModel("tiny", device=device, compute_type="int8")
        
        print(f"✓ Successfully loaded Whisper 'tiny' model on {device}")
        return True
    except Exception as e:
        print(f"✗ Failed to load Whisper model: {str(e)}")
        return False

if __name__ == "__main__":
    print("Whisper Diarization - Dependency Test")
    print("=" * 60)
    print()
    
    imports_ok = test_imports()
    
    if imports_ok:
        model_ok = test_whisper_model()
        
        if model_ok:
            print("\n" + "=" * 60)
            print("🎉 Setup complete! You can now:")
            print("  1. Run: python backend/app.py")
            print("  2. Open: http://localhost:5000")
            print("  3. Upload audio and transcribe!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n⚠️  Warning: Model loading failed, but core imports work.")
            print("   You may need to download models on first use.")
            sys.exit(1)
    else:
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
