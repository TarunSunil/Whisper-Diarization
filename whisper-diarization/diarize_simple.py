"""
Simplified diarization script using pyannote.audio
This script provides speaker diarization without requiring ctc-forced-aligner
"""
import argparse
import json
import os
import sys
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Disable CUDA to avoid GPU-related errors on CPU-only systems
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import torch
from faster_whisper import WhisperModel

# Import pyannote with error handling
try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    print("Warning: pyannote.audio not available. Diarization will be skipped.")

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def transcribe_with_whisper(audio_path, model_name="base", device="cpu", language=None):
    """Transcribe audio using faster-whisper"""
    print(f"Loading Whisper model: {model_name}")
    
    compute_type = "int8" if device == "cpu" else "float16"
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    
    print(f"Transcribing audio: {audio_path}")
    segments, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        word_timestamps=True
    )
    
    # Extract segments with timestamps
    transcription = []
    for segment in segments:
        transcription.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "words": [
                {
                    "word": word.word,
                    "start": word.start,
                    "end": word.end
                }
                for word in segment.words
            ] if hasattr(segment, 'words') and segment.words else []
        })
    
    return transcription, info

def diarize_audio(audio_path, hf_token=None):
    """Perform speaker diarization using pyannote.audio"""
    print("Loading diarization model...")
    
    if not PYANNOTE_AVAILABLE:
        print("Pyannote not available, skipping diarization...")
        return None
    
    try:
        # Force CPU to avoid CUDA issues on systems without GPU
        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Disable CUDA
        
        device = torch.device("cpu")  # Force CPU
        
        if hf_token:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=hf_token
            )
        else:
            # Try without token (will fail if model requires authentication)
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1"
            )
        
        # Move to device
        if pipeline is not None and hasattr(pipeline, 'to'):
            pipeline.to(device)
        
        print(f"Running diarization on: {audio_path}")
        if pipeline is not None:
            diarization = pipeline(audio_path)
        else:
            raise Exception("Failed to initialize pipeline")
        
        # Convert to list of segments
        speaker_segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        
        return speaker_segments
    
    except Exception as e:
        print(f"Diarization failed: {str(e)}")
        print("\nNote: pyannote models require a Hugging Face token.")
        print("Get one at: https://huggingface.co/settings/tokens")
        print("Then accept the terms at: https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("\nFor now, returning single speaker...")
        return None

def assign_speakers_to_transcript(transcription, speaker_segments):
    """Assign speakers to transcription segments"""
    if not speaker_segments:
        # No diarization, assign all to Speaker 1
        for segment in transcription:
            segment["speaker"] = "SPEAKER_00"
        return transcription
    
    # Assign speaker to each segment based on overlap
    for segment in transcription:
        segment_mid = (segment["start"] + segment["end"]) / 2
        
        # Find the speaker segment that contains this timestamp
        assigned_speaker = "SPEAKER_00"
        for sp_seg in speaker_segments:
            if sp_seg["start"] <= segment_mid <= sp_seg["end"]:
                assigned_speaker = sp_seg["speaker"]
                break
        
        segment["speaker"] = assigned_speaker
    
    return transcription

def generate_outputs(transcription, output_dir, audio_name):
    """Generate output files (TXT, SRT, JSON)"""
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = Path(audio_name).stem
    
    # Generate TXT
    txt_path = os.path.join(output_dir, f"{base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        current_speaker = None
        for segment in transcription:
            if segment["speaker"] != current_speaker:
                current_speaker = segment["speaker"]
                f.write(f"\n[{current_speaker}]\n")
            f.write(segment["text"] + " ")
    
    print(f"Saved transcript: {txt_path}")
    
    # Generate SRT
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    with open(srt_path, "w", encoding="utf-8", errors="replace") as f:
        for i, segment in enumerate(transcription, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n")
            f.write(f"[{segment['speaker']}] {segment['text']}\n\n")
    
    print(f"Saved SRT: {srt_path}")
    
    # Generate JSON
    json_path = os.path.join(output_dir, f"{base_name}.json")
    with open(json_path, "w", encoding="utf-8", errors="replace") as f:
        json.dump(transcription, f, indent=2, ensure_ascii=False)
    
    print(f"Saved JSON: {json_path}")
    
    return txt_path, srt_path, json_path

def main():
    parser = argparse.ArgumentParser(description="Simplified audio transcription with speaker diarization")
    parser.add_argument("--audio-files", nargs="+", required=True, help="Path to audio file(s)")
    parser.add_argument("--whisper-model", default="base", help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--device", default="cpu", help="Device to use (cpu/cuda)")
    parser.add_argument("--language", default=None, help="Language code (e.g., en, es, fr)")
    parser.add_argument("--hf-token", default=None, help="Hugging Face token for pyannote models")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument("--no-diarization", action="store_true", help="Skip speaker diarization")
    
    args = parser.parse_args()
    
    for audio_path in args.audio_files:
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found: {audio_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing: {audio_path}")
        print(f"{'='*60}\n")
        
        # Step 1: Transcribe with Whisper
        transcription, info = transcribe_with_whisper(
            audio_path,
            model_name=args.whisper_model,
            device=args.device,
            language=args.language
        )
        
        print(f"\nDetected language: {info.language} (probability: {info.language_probability:.2f})")
        print(f"Duration: {info.duration:.2f} seconds")
        print(f"Segments: {len(transcription)}")
        
        # Step 2: Diarization (optional)
        speaker_segments = None
        if not args.no_diarization:
            speaker_segments = diarize_audio(audio_path, args.hf_token)
        
        # Step 3: Assign speakers to transcript
        transcription = assign_speakers_to_transcript(transcription, speaker_segments)
        
        # Step 4: Generate outputs
        txt_path, srt_path, json_path = generate_outputs(
            transcription,
            args.output_dir,
            os.path.basename(audio_path)
        )
        
        print(f"\n[OK] Processing complete for: {audio_path}")
    
    print(f"\n{'='*60}")
    print("All files processed successfully!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
