import subprocess

def download(url):
    video_details = None
    print(f"[Info]: Downloading Youtube Details at: {url}")
    process = subprocess.Popen(
        ["yt-dlp", url, "--skip-download", "--print-json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    
    # Lazy approach, assumes last stdout text is video details
    for line in process.stdout:
        video_details = line

    for line in process.stderr:
        print(f"[Error]: {line}")

    process.wait()
    if process.returncode == 0:
        print("Download complete!")
        return video_details
    else:
        print("An error occurred during the download.")
        return None
