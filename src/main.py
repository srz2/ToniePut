import os
import shutil
from flask import Flask, render_template, request, redirect
import downloaders.download_spotify as spotify
import downloaders.download_youtube as youtube
from tonie_api.api import TonieAPI

app = Flask(__name__)

user = None

def move_file(file):
    global user
    print(f"[Info]: User {user} moving file {file}")
    shutil.move(file, f"{user['upload_path']}/{file}")

def save_file(file):
    print(f"[Info]: Saving file {file}")
    global user
    file.save(f"{user['upload_path']}/{file.filename}")

def rename_file(current_file, new_name):
    global user
    cur_file = f"{user['upload_path']}/{current_file}"
    new_file = f"{user['upload_path']}/{new_name}"
    print(f"[Info]: Renaming file {cur_file} to {new_file}")
    os.rename(cur_file, new_file)

def get_pending_files():
    global user
    if user == None:
        return []
    files = os.listdir(user['upload_path'])
    filtered_files = []
    for file in files:
        if not file.endswith('.mp3'):
            continue
        filtered_files.append(file)
    return filtered_files

def delete_file(target_file):
    global user
    files = get_pending_files()
    if not target_file in files:
        raise FileNotFoundError()
    filename = f"{user['upload_path']}/{target_file}"
    os.remove(filename)

@app.route("/")
def index():
    global user
    email = ''
    if user != None:
        email = user['profile'].email
        print(f"Current user is {email}")
    files = get_pending_files()
    tonies = get_creative_tonies('objects')
    return render_template('index.html', files=files, tonies=tonies, username=email)

@app.route("/mytonie-login", methods=["POST"])
def tonie_login():
    username = request.form.get('username')
    password = request.form.get('password')
    api = TonieAPI(username, password)
    profile = api.get_me()
    if profile == None:
        print("[Error]: Failed to login")
        return redirect("/")
    global user
    user = {
        "profile": profile,
        "credentials": {
            "username": username,
            "password": password
        },
        "upload_path": f"upload_to_tonie/{profile.uuid}",
    }
    
    # Create directory for user if it doesnt exist
    os.makedirs(user['upload_path'], exist_ok=True)

    return redirect('/')

@app.route("/logout", methods=["POST"])
def tonie_logout():
    global user
    user = None
    return redirect('/')

@app.route("/get-tonies", methods=["GET"])
def get_creative_tonies(return_type=''):
    global user
    if user == None:
        return []
    api = TonieAPI(user['credentials']['username'], user["credentials"]['password'])
    house = api.get_households()[0]
    tonies = api.get_all_creative_tonies_by_household(house)
    return tonies

@app.route("/youtube", methods=["POST"])
def process_Youtube():
    url = request.form['url_youtube']
    song_name = youtube.download(url)
    if not song_name:
        return render_template("/error.html", message='Failed to download youtube video')
    move_file(song_name)
    return redirect("/")

@app.route("/spotify", methods=["POST"])
def process_spotify():
    url = request.form['url_spotify']
    song_name = spotify.download(url)
    if not song_name:
        return render_template("/error.html", message='Failed to download spotify video')
    move_file(song_name)
    return redirect("/")

@app.route("/upload", methods=["POST"])
def process_Local():
    file = request.files['file']
    if file.filename == '':
        return 'No selected files'
    save_file(file)
    return redirect("/")

@app.route("/delete_pending_file", methods=["POST"])
def delete_pending_file():
    file_name = request.args.get('filename')
    delete_file(file_name)
    return redirect("/")

@app.route("/rename_pending_file", methods=["POST"])
def rename_pending_file():
    file_name = request.args.get('filename')
    new_name = request.form.get('new-name')
    if not new_name.endswith('.mp3'):
        new_name += ".mp3"
    rename_file(file_name, new_name)
    return redirect("/")

@app.route('/load-tonie', methods=["POST"])
def load_tonie():
    global user
    if user == None:
        return redirect("/")
    selected_tonie_id = request.form.get('selected-tonie')
    files = get_pending_files()
    api = TonieAPI(user['credentials']['username'], user["credentials"]['password'])
    house = api.get_households()[0]

    # Get tonie with matching Id
    tonies = list(filter(lambda tonie: (tonie.id == selected_tonie_id), api.get_all_creative_tonies_by_household(house)))
    if len(tonies) == 0:
        return "Failed to find selected tonie"
    
    selected_tonie = tonies[0]
    for file in files:
        relative_file = f"{user['upload_path']}/{file}"
        api.upload_file_to_tonie(selected_tonie, relative_file, file[0:len(file) - 4])
        delete_file(file)
        print(f"Upload file {file}")
    return redirect('/')

if __name__ == "__main__":
    app.run()