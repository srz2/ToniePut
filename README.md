ToniePut
========

![Docker Image Version](https://img.shields.io/docker/v/srz2/tonieput?label=Docker%20Image&link=https%3A%2F%2Fhub.docker.com%2Frepository%2Fdocker%2Fsrz2%2Ftonieput%2Fgeneral)

# Introduction
ToniePut is a utility to allow you to connect to your [TonieBox](https://tonies.com/) and upload MP3 files to the box sourced either from youtube, spotifiy, or local files

# How to Use
1. Log in with your MyTonies `username` and `password`
2. Load your files by submitting youtube/spotify links or load a local file (only MP3s allowed currently)
3. Verify your pending files
4. Select your desired CreativeTonie to load your files to
5. Selected the `Load` button

# Resources Used

For simplicity, utilities used are configured to download the audio files as an MP3 file. Also local files are restricted to MP3 files.

## Youtube Downloads

In order to download the audio of youtube videos, [yt-dlp](https://github.com/yt-dlp/yt-dlp) is used.

## Spotify

In order to download the audio files of a Spotify song, [spotdp](https://github.com/spotDL/spotify-downloader) is used. 

# How to Build

## Docker 
To Build a docker image, use the following command

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t {name}/tonieput:{tag} .
```

# How to Run

## Local
To build locally, use the following command

```bash
gunicorn --certfile ../cert.pem --keyfile ../key.pem -b 0.0.0.0:5050 --chdir src main:app
```

## Linux
This needs two volumes:
1. Location for cert.pem and key.pem at `/var/lib/tonieput/certs`
2. Location for user data at `/var/lib/tonieput/data`

```bash
docker run \
-v /var/lib/tonieput/certs:/app/certs \
-v /var/lib/tonieput/data:/app/upload_to_tonie \
-p 5000:8000 \
-d \
[Docker_Image]
```
