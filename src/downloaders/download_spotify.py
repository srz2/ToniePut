import subprocess

def download(url):
    song_name = None
    print(f"[Info]: Downloading Spotify at: {url}")
    process = subprocess.Popen(
        ["spotdl", url, "--format", "mp3", "--overwrite", "force", "--cookie-file", "assets/cookies-spotify.txt", "--yt-dlp-args", "--cookies assets/cookies-youtube.txt", "--print-errors", "--log-level", "DEBUG"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    
    for line in process.stdout:
        print(line, end="")  # Print each line as it's received
        if line.startswith('Downloaded '):
            start = line.find("\"") + 1
            # Find second the last colon
            end = line.rfind(":", 0, line.rfind(":")) - 1
            song_name = line[start:end] + ".mp3"

    for line in process.stderr:
        print(f"[Error]: {line}")

    process.wait()
    if process.returncode == 0:
        print("Download complete!")
        return song_name
    else:
        print("An error occurred during the download.")
        return None
