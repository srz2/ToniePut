import subprocess

def download_song_with_output(url):
    process = subprocess.Popen(
        ["yt-dlp", url, "-x", "--audio-format", "mp3", "--print", "filename", "-o", "%(title)s.%(ext)s", "--no-simulate"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    
    for line in process.stdout:
        song_name = line

    process.wait()
    if process.returncode == 0:
        print("Download complete!")
        return song_name[0:len(song_name) - 6] + ".mp3"
    else:
        print("An error occurred during the download.")

# Example usage - Spotify
song_name = download_song_with_output('https://www.youtube.com/watch?v=i5L9xEk_adw')
print('Completed retrieval of ' + song_name)
