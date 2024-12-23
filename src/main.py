import os
import math
import json
import pickle
from flask import Flask, render_template, request, redirect, session
import downloaders.download_spotify as spotify
import downloaders.download_youtube as youtube
import downloaders.download_youtube_details as yt_details
from tonie_api.api import TonieAPI

app = Flask(__name__)
app.secret_key = os.getenv('session-secret', 'secret-key')

def get_user():
    if 'user' in session:
        user_pickle = session['user']
        if user_pickle:
            user = pickle.loads(user_pickle.encode('latin1'))
            return user
        return "No user in session."
    else:
        return None
    
def get_api_client():
    user = get_user()
    if not user:
        return None
    api : TonieAPI = user['api']['client']
    api.session.token = user['api']['active-session-token']
    return api

def save_file(file):
    print(f"[Info]: Saving file {file}")
    user = get_user()
    file.save(f"{user['upload_path']}/{file.filename}")

def rename_file(current_file, new_name):
    user = get_user()
    cur_file = f"{user['upload_path']}/{current_file}"
    new_file = f"{user['upload_path']}/{new_name}"
    print(f"[Info]: Renaming file {cur_file} to {new_file}")
    os.rename(cur_file, new_file)

def get_pending_files():
    user = get_user()
    if user == None:
        return []
    user_file_path = user['upload_path']

    # Issue logout of path does not exist
    if not os.path.isdir(user_file_path):
        tonie_logout()
        raise LookupError()

    files = os.listdir(user_file_path)
    filtered_files = []
    for file in files:
        if not file.endswith('.mp3'):
            continue
        filtered_files.append(file)
    return filtered_files

def delete_file(target_file):
    user = get_user()
    files = get_pending_files()
    if not target_file in files:
        raise FileNotFoundError()
    filename = f"{user['upload_path']}/{target_file}"
    os.remove(filename)

def convert_to_seconds(time_str):
    # Split the time string into components
    parts = list(map(int, time_str.split(":")))
    
    # Calculate total seconds based on the number of components
    if len(parts) == 3:  # Format is HH:MM:SS
        hours, minutes, seconds = parts
        total_seconds = hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:  # Format is MM:SS
        minutes, seconds = parts
        total_seconds = minutes * 60 + seconds
    else:
        raise ValueError("Invalid time format. Use MM:SS or HH:MM:SS.")
    
    return total_seconds

def get_file_size_mb(file):
    # Seek to the end of the file to find its size in bytes
    file.stream.seek(0, 2)  # Move to the end of the file
    size_in_bytes = file.stream.tell()  # Get the current position (file size in bytes)
    file.stream.seek(0)  # Reset the stream pointer to the beginning
    
    # Convert bytes to megabytes
    size_in_mb = size_in_bytes / (1024 * 1024)
    return size_in_mb

def createClient(username: str, password: str) -> TonieAPI:
    try:
        api = TonieAPI(username, password)
        return api
    except Exception:
        print('[Error]: Failed to create client')
        return None

def logout_user():
    if 'user' in session.keys():
        session.pop('user')

@app.route("/")
def index():
    user = get_user()

    # Get information for user
    files = get_pending_files()
    tonies = get_creative_tonies()
    
    # Render information to user
    return render_template('index.html', files=files, tonies=tonies, username= None if user == None else user['profile'].email)

@app.route("/mytonie-login", methods=["POST"])
def tonie_login():
    username = request.form.get('username')
    password = request.form.get('password')
    api = createClient(username, password)
    if not api:
        return render_template("loginfail.html", message="Login credentials are incorrect")
    
    # Get profile for user
    profile = api.get_me()
    if profile == None:
        print("[Error]: Failed to login")
        return render_template("loginfail.html", message="Failed to log into TonieBox Api")

    # Save user information
    user = {
        "profile": profile,
        "api": {
            "client" : api,
            "active-session-token" : api.session.token
        },
        "upload_path": f"upload_to_tonie/{profile.uuid}",
    }
    session['user'] = pickle.dumps(user).decode('latin1')
    
    # Create directory for user if it doesnt exist
    os.makedirs(user['upload_path'], exist_ok=True)

    return redirect('/')

@app.route("/logout", methods=["POST"])
def tonie_logout():
    logout_user()
    return redirect('/')

@app.route("/get-tonies", methods=["GET"])
def get_creative_tonies():
    api = get_api_client()
    if api == None:
        return []
    houses = api.get_households()
    if len(houses) == 0:
        return list()
    
    # TODO: Create way to work with multiple houses
    house = houses[0]
    
    tonies = api.get_all_creative_tonies_by_household(house)
    return tonies

@app.route("/download", methods=["POST"])
def process_download_link():
    url = request.form['url']
    if 'youtube.com' in url or 'youtu.be' in url:
        return process_youtube(url)
    elif 'spotify.com' in url:
        return process_spotify(url)
    else:
        return render_template("/error.html", message='Unsupported Url download source mechanism')

def process_youtube(url):
    if not url:
        return render_template("/error.html", message='No Url provided for youtube download request')
    
    # remove si if it exists
    # https://youtu.be/8tDOeQqnrYQ?si=ja8546dJrQG2tqPV
    if "?" in url:
        pos = url.index("?")
        url = url[0:pos]

    user = get_user()
    # Get video deatils first
    MAX_DURATION = 1200 # seconds
    MAX_DURATION_LONG = f"{math.ceil(MAX_DURATION / 60)} Minutes"
    details = yt_details.download(url)
    if not details:
        return render_template('/error.html', message="Failed to download youtube video details")
    obj = json.loads(details)
    duration_str = obj['duration_string']
    seconds = convert_to_seconds(duration_str)
    if seconds > MAX_DURATION:
        error_msg = f"Video Duration: {duration_str} or {seconds} seconds. Failing, outside max duration of {MAX_DURATION_LONG}"
        print(error_msg)
        return render_template('/error.html', message=error_msg)

    song_name = youtube.download(url, user['upload_path']+"/")
    if not song_name:
        return render_template("/error.html", message='Failed to download youtube video')
    return redirect("/")

def process_spotify(url: str):
    if not url:
        return render_template("/error.html", message='No Url provided for spotifiy download request')
    
    # remove si if it exists
    # https://open.spotify.com/track/4KBCelgd9JynmV0DpWjYJA?si=30639a7ff023439a
    if "?" in url:
        pos = url.index("?")
        url = url[0:pos]

    user = get_user()
    song_name = spotify.download(url, user['upload_path']+"/")
    if not song_name:
        return render_template("/error.html", message='Failed to download spotify song')
    return redirect("/")

@app.route("/upload", methods=["POST"])
def process_Local():
    file = request.files['file']
    if file.filename == '':
        return 'No selected files'
    
    # Only accept MP3s
    if not file.filename.endswith('.mp3'):
        return render_template('/error.html', message="Invalid file type, only MP3 is allowed")
    
    # Check upload file size
    MAX_SIZE_MB = 10.0
    size = get_file_size_mb(file)
    if size > MAX_SIZE_MB:
        error_msg = f"File is too large at {math.trunc(size)} MB, max size is {MAX_SIZE_MB} MB"
        print(error_msg)
        return render_template('/error.html', message=error_msg)

    save_file(file)
    return redirect("/")

@app.route("/delete_pending_file", methods=["POST"])
def delete_pending_file():
    file_name = request.args.get('filename')
    delete_file(file_name)
    return redirect("/")

@app.route("/rename_pending_file", methods=["POST"])
def rename_pending_file():
    file_name = request.form.get('current_song')
    new_name = request.form.get('new-name').rstrip()

    # Ignore empty name
    if new_name.rstrip() == '':
        return redirect('/')

    if not new_name.endswith('.mp3'):
        new_name += ".mp3"

    # Ignore same name
    if new_name == file_name:
        return redirect('/')

    rename_file(file_name, new_name)
    return redirect("/")

@app.route('/load-tonie', methods=["POST"])
def load_tonie():
    user = get_user()
    if user == None:
        return redirect("/")
    selected_tonie_id = request.form.get('selected-tonie')
    files = get_pending_files()
    api = get_api_client()
    house = api.get_households()[0]

    # Get tonie with matching Id
    tonies = list(filter(lambda tonie: (tonie.id == selected_tonie_id), api.get_all_creative_tonies_by_household(house)))
    if len(tonies) == 0:
        return render_template('error.html', message="Failed to find selected tonie")
    
    selected_tonie = tonies[0]
    for file in files:
        relative_file = f"{user['upload_path']}/{file}"
        api.upload_file_to_tonie(selected_tonie, relative_file, file[0:len(file) - 4])
        delete_file(file)
        print(f"Upload file {file}")
    return redirect('/')

if __name__ == "__main__":
    app.run()
