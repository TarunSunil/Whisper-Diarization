import sys
import subprocess
import pkg_resources

def check_requirements(requirements_file='requirements.txt'):
    print(f"Checking requirements from {requirements_file}...")
    
    with open(requirements_file, 'r') as f:
        lines = f.readlines()
    
    missing = []
    installed = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Handle git requirements
        if line.startswith('git+'):
            pkg_name = line.split('/')[-1].replace('.git', '')
            # This is a simplification, git repos might have different package names
            # We'll just check if we can import it or if pip shows it
            # For now, let's skip strict checking of git urls in this simple script
            # or try to guess the package name.
            if 'demucs' in pkg_name: pkg_name = 'demucs'
            elif 'deepmultilingualpunctuation' in pkg_name: pkg_name = 'deepmultilingualpunctuation'
            elif 'ctc-forced-aligner' in pkg_name: pkg_name = 'ctc_forced_aligner'
            
            try:
                pkg_resources.get_distribution(pkg_name)
                installed.append(line)
                print(f"✅ {pkg_name} is installed")
            except pkg_resources.DistributionNotFound:
                missing.append(line)
                print(f"❌ {pkg_name} is MISSING")
            continue

        # Handle normal requirements
        # Remove version specifiers for simple checking
        pkg_name = line.split('>')[0].split('<')[0].split('=')[0].split('[')[0]
        
        try:
            pkg_resources.get_distribution(pkg_name)
            installed.append(line)
            print(f"✅ {pkg_name} is installed")
        except pkg_resources.DistributionNotFound:
            missing.append(line)
            print(f"❌ {pkg_name} is MISSING")

    # Check for FFmpeg
    print("-" * 40)
    print("Checking for FFmpeg...")
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("✅ FFmpeg is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg is MISSING")
        print("Please install FFmpeg and add it to your PATH.")
        print("Download from: https://ffmpeg.org/download.html")
        # We don't exit here, but we warn
        
    print("-" * 40)
    if missing:
        print(f"Found {len(missing)} missing requirements.")
        print("Run the following command to install them:")
        print(f"pip install -r {requirements_file}")
        sys.exit(1)
    else:
        print("All requirements are installed!")
        sys.exit(0)

if __name__ == "__main__":
    check_requirements()
