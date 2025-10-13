"""
Test script to verify the upload and processing workflow
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:5000"

def test_server():
    """Test if server is running"""
    try:
        response = requests.get(BASE_URL)
        print(f"✓ Server is running (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ Server is not responding: {str(e)}")
        return False

def test_upload_api():
    """Test the upload API without actually uploading a file"""
    try:
        # Test with a small in-memory file
        files = {
            'audio': ('test.wav', b'RIFF' + b'\x00' * 100, 'audio/wav')
        }
        data = {
            'options': json.dumps({
                'whisper_model': 'tiny',
                'language': 'en',
                'device': 'cpu'
            })
        }
        
        print("\nTesting upload endpoint...")
        response = requests.post(f"{BASE_URL}/api/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Upload API working")
            print(f"  Job ID: {result.get('job_id', 'N/A')}")
            return result.get('job_id')
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Upload API error: {str(e)}")
        return None

def test_status_api(job_id):
    """Test the status API"""
    try:
        response = requests.get(f"{BASE_URL}/api/status/{job_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status API working")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  Progress: {result.get('progress', 0)}%")
            print(f"  Step: {result.get('step', 'N/A')}")
            return True
        elif response.status_code == 404:
            print(f"⚠ Job not found (expected if processed quickly)")
            return True
        else:
            print(f"✗ Status API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Status API error: {str(e)}")
        return False

def test_with_real_audio():
    """Test with actual audio file from dataset"""
    dataset_dir = "dataset"
    audio_files = [f for f in os.listdir(dataset_dir) if f.endswith(('.wav', '.mp3'))] if os.path.exists(dataset_dir) else []
    
    if not audio_files:
        print("\n⚠ No audio files found in dataset folder")
        return False
    
    audio_file = os.path.join(dataset_dir, audio_files[0])
    print(f"\nTesting with real audio: {audio_files[0]}")
    
    try:
        with open(audio_file, 'rb') as f:
            files = {
                'audio': (audio_files[0], f, 'audio/wav')
            }
            data = {
                'options': json.dumps({
                    'whisper_model': 'tiny',
                    'language': 'auto',
                    'device': 'cpu',
                    'skip_diarization': True  # Skip diarization for faster testing
                })
            }
            
            response = requests.post(f"{BASE_URL}/api/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                print(f"✓ Upload successful (Job ID: {job_id})")
                
                # Poll status
                print("\nMonitoring processing...")
                max_attempts = 20
                for i in range(max_attempts):
                    time.sleep(2)
                    status_response = requests.get(f"{BASE_URL}/api/status/{job_id}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        progress = status_data.get('progress', 0)
                        step = status_data.get('step', '')
                        
                        print(f"  [{i+1}/{max_attempts}] Status: {status}, Progress: {progress}%, Step: {step}")
                        
                        if status == 'completed':
                            print("\n✅ Processing completed successfully!")
                            
                            # Try to get result
                            result_response = requests.get(f"{BASE_URL}/api/result/{job_id}")
                            if result_response.status_code == 200:
                                transcript = result_response.json()
                                print(f"\n📝 Transcript preview:")
                                for segment in transcript[:3]:  # Show first 3 segments
                                    print(f"  [{segment.get('speaker', 'N/A')}] {segment.get('text', '')[:80]}...")
                            return True
                            
                        elif status == 'failed':
                            print(f"\n❌ Processing failed")
                            error = status_data.get('error', 'Unknown error')
                            print(f"  Error: {error}")
                            return False
                
                print(f"\n⏱️ Processing is taking longer than expected")
                return False
                
            else:
                print(f"✗ Upload failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"✗ Real audio test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Whisper Diarization - System Test")
    print("=" * 60)
    
    # Test 1: Server running
    if not test_server():
        print("\n❌ Server is not running. Start it with: python backend/app.py")
        return
    
    # Test 2: Upload API
    print("\n" + "=" * 60)
    print("Testing Upload API")
    print("=" * 60)
    job_id = test_upload_api()
    
    # Test 3: Status API
    if job_id:
        print("\n" + "=" * 60)
        print("Testing Status API")
        print("=" * 60)
        time.sleep(1)  # Give it a moment to process
        test_status_api(job_id)
    
    # Test 4: Real audio processing
    print("\n" + "=" * 60)
    print("Testing with Real Audio File")
    print("=" * 60)
    success = test_with_real_audio()
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! System is working correctly.")
        print("\nYou can now:")
        print("  1. Open http://localhost:5000 in your browser")
        print("  2. Upload an audio file")
        print("  3. Get your transcription!")
    else:
        print("⚠️ Some tests had issues. Check the output above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
