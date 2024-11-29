import subprocess

def download(url, output_dir):
    song_name = None
    print(f"[Info]: Downloading Youtube at: {url}")
    process = subprocess.Popen(
        ["yt-dlp", url, "-x", "--audio-format", "mp3", "--print", "filename", "-o", f"{output_dir}/%(title)s.%(ext)s", "--no-simulate", "--cookies", "assets/cookies-youtube.txt", "-v"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    
    for line in process.stdout:
        song_name = line
    for line in process.stderr:
        print(f"[Error]: {line}")

    process.wait()
    if process.returncode == 0:
        print("Download complete!")
        return song_name[0:len(song_name) - 6] + ".mp3"
    else:
        print("An error occurred during the download.")
        return None
