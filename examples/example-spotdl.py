import subprocess

def download_song_with_output(url):
    process = subprocess.Popen(
        ["spotdl", url, "--format", "mp3", "--overwrite", "force"],
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

    process.wait()
    if process.returncode == 0:
        print("Download complete!")
        return song_name
    else:
        print("An error occurred during the download.")

# Example usage - Spotify
song_name = download_song_with_output('https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2?si=825f96a84a204d8a')
print('Completed retrieval of ' + song_name)
