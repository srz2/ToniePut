import os
import shutil
import pickle
from flask import Flask, render_template, request, redirect, session
import downloaders.download_spotify as spotify
import downloaders.download_youtube as youtube
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

def move_file(file):
    user = get_user()
    print(f"[Info]: Moving file {file}")
    shutil.move(file, f"{user['upload_path']}/{file}")

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
    files = os.listdir(user['upload_path'])
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

@app.route("/")
def index():
    user = get_user()

    # User is logged in, get user information
    files = get_pending_files()
    tonies = get_creative_tonies()
    return render_template('index.html', files=files, tonies=tonies, username= None if user == None else user['profile'].email)

@app.route("/mytonie-login", methods=["POST"])
def tonie_login():
    username = request.form.get('username')
    password = request.form.get('password')
    api = TonieAPI(username, password)
    profile = api.get_me()
    if profile == None:
        print("[Error]: Failed to login")
        return render_template("error.html", message="Failed to log into TonieBox Api")

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
    session.pop('user')
    return redirect('/')

@app.route("/get-tonies", methods=["GET"])
def get_creative_tonies():
    api = get_api_client()
    if api == None:
        return []
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