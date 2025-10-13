import requests
import time

job_id = "3264995c-b016-4d33-9678-6fee29d8100c"
BASE_URL = "http://localhost:5000"

print(f"Monitoring job: {job_id}\n")

for i in range(60):  # Check for 5 minutes
    try:
        response = requests.get(f"{BASE_URL}/api/status/{job_id}")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            progress = data.get('progress', 0)
            step = data.get('step', '')
            
            print(f"[{i+1}] Status: {status}, Progress: {progress}%, Step: {step}")
            
            if status == 'completed':
                print("\n✅ COMPLETED!")
                result_resp = requests.get(f"{BASE_URL}/api/result/{job_id}")
                if result_resp.status_code == 200:
                    transcript = result_resp.json()
                    print(f"\nTranscript has {len(transcript)} segments")
                    for seg in transcript[:3]:
                        print(f"  [{seg['speaker']}] {seg['text'][:100]}...")
                break
            elif status == 'failed':
                print(f"\n❌ FAILED: {data.get('error', 'Unknown error')}")
                break
        else:
            print(f"[{i+1}] Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"[{i+1}] Error: {str(e)}")
    
    time.sleep(5)
