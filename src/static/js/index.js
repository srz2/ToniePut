const popupRename = document.getElementById('popup-rename');
const renameForm = popupRename.querySelector("form");
const popupRenameClose = document.getElementById('popup-rename-close');
const containers = document.getElementsByClassName('content-wrapper')
const btnRenameSongs = document.getElementsByClassName('song-rename-button')
const currentSong = document.getElementById('current_song');
const currentSongHidden = document.getElementById('current_song_hidden');
const loader = document.querySelector('.loader-container');
const linkForm = document.getElementById('link-form');
const fileForm = document.getElementById('file-form');

// Add onclick listeners to each rename button
for (let c = 0; c < btnRenameSongs.length; c++){
    btnRenameSongs[c].addEventListener('click', (event) => {
        popupRename.style.display = 'flex'
        document.body.classList.add('overlay-active')

        const selectedSongElement = event.target.parentElement.querySelector('p');
        selected_song = selectedSongElement.textContent;
        currentSong.textContent = selected_song;
        currentSongHidden.value = selected_song;

        // Disable all containers
        toggleContainers(false);
    })
}

// Add close logic
popupRenameClose.addEventListener('click', () => {
    popupRename.style.display = 'none';
    toggleContainers(true)
});

function toggleContainers(isEnabled){
    for (let z = 0; z < containers.length; z++){
        containers[z].style['pointer-events'] = isEnabled ? 'auto' : 'none';
    }
}

// Show loader logic
linkForm.addEventListener('submit', (e) => {
  e.preventDefault();
  loader.style.display = 'block';
  setTimeout(() => linkForm.submit(), 100); // Small delay to allow DOM update
});
fileForm.addEventListener('submit', (e) => {
  e.preventDefault();
  loader.style.display = 'block';
  setTimeout(() => fileForm.submit(), 100); // Small delay to allow DOM update
});
