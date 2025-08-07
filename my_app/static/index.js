window.addEventListener('DOMContentLoaded', () => {
    // Add loader to the start button
    const cardContainerEl = document.querySelector('.card-container');
    const startBtnEl = document.querySelector('.start-btn');
    const loaderEl = document.querySelector('.loader');
    const startBtnText = document.querySelector('.start-text');
    const qualitySelect = document.querySelector('#quality');
    const urlInput = document.querySelector('.url-input');
    const downloadVideoBtn = document.querySelector('.video-download-btn');
    const downloadAudioBtn = document.querySelector('#audio-download-btn');

    // Disable the start button when the DOM content is loaded
    startBtnEl.disabled = true
    if(startBtnEl.disabled == true){
        startBtnEl.classList.remove('bg-gray-900');
        startBtnEl.classList.add('bg-gray-400');
        startBtnEl.classList.remove('cursor-pointer');
        startBtnEl.classList.remove('hover:bg-gray-800');
        startBtnEl.classList.add('cursor-not-allowed');
    }
    // Activate the start button
    urlInput.addEventListener('keydown', () => {
        startBtnEl.disabled = false;
        if(startBtnEl.disabled == false){
            startBtnEl.classList.add('bg-gray-900');
            startBtnEl.classList.remove('bg-gray-400');
            startBtnEl.classList.add('cursor-pointer');
            startBtnEl.classList.add('hover:bg-gray-800');
            startBtnEl.classList.remove('cursor-not-allowed');

            startBtnEl.addEventListener('click', () => {
                if(cardContainerEl == null){
                    loaderEl.classList.remove('hide');
                    startBtnText.classList.add('hide');
                }else{
                    loaderEl.classList.add('hide');
                    startBtnText.classList.remove('hide');
                }
            });
        }
    })

    // show and hide audio and video containers when the buttons have clicked
    const audioBtnEl = document.querySelector('.js-audio-button');
    const videoBtnEl = document.querySelector('.js-video-button');
    const videoContainerEl = document.querySelector('.js-video-container');
    const audioContainerEl = document.querySelector('.js-audio-container');

    // Add event on click to toggle between the containers
    // Show audio container
    audioBtnEl.addEventListener('click', () => {
        if(videoBtnEl.classList.contains('bg-gray-900')){
            videoBtnEl.classList.remove('bg-gray-900');
            videoBtnEl.classList.remove('text-white');
            videoBtnEl.classList.add('text-gray-900');
            audioBtnEl.classList.add('bg-gray-900');
            audioBtnEl.classList.add('text-white');
            audioContainerEl.classList.remove('hide');
            videoContainerEl.classList.add('hide');
        }
    });
    // Show video container
    videoBtnEl.addEventListener('click', () => {
        if(audioBtnEl.classList.contains('bg-gray-900')){
            audioBtnEl.classList.remove('bg-gray-900');
            audioBtnEl.classList.remove('text-white');
            audioBtnEl.classList.add('text-gray-900');
            videoBtnEl.classList.add('bg-gray-900');
            videoBtnEl.classList.add('text-white');
            videoContainerEl.classList.remove('hide');
            audioContainerEl.classList.add('hide');
        }
    });

    // pass the video quality to the socket
    const downloadForm = document.querySelector('form');
    const progressBar = document.querySelector('.progress-bar');
    const progressFill = document.querySelector('#progress-fill');
    const statusMessage = document.querySelector('#status-message');
    const closeProgressBtn = document.querySelector('.js-close-btn');
    const popUpContainer = document.querySelector('#progress-container');

    // Connect to the SocketIO server
    const socket = io();

    // Download video
    downloadVideoBtn.addEventListener('click', (e) => {
        e.preventDefault();

        const url = urlInput.value.trim();
        const quality = qualitySelect.value;

        if(!quality || quality === ""){
            alert("Please select a valid video quality.")
            return
        }
        if (url) {
            // Display initial status message
            popUpContainer.classList.remove('hide')
            statusMessage.textContent = 'Processing request...';
            statusMessage.className = 'message info';
            statusMessage.style.display = 'block';
            progressBar.style.display = 'block';
            
            // Reset progress bar
            progressFill.style.width = '0%';
            progressFill.textContent = '';

            const FILE_TYPE = 'Video';
            
            // Emit the request to the backend
            socket.emit('download_request', { url: url, quality: quality, file: FILE_TYPE });
            
            // Disable the button to prevent multiple requests
            downloadVideoBtn.disabled = true;
            if(downloadVideoBtn.disabled == true){
                downloadVideoBtn.classList.remove('bg-gray-900');
                downloadVideoBtn.classList.add('bg-gray-400');
                downloadVideoBtn.classList.remove('cursor-pointer');
                downloadVideoBtn.classList.remove('hover:bg-gray-800');
                downloadVideoBtn.classList.add('cursor-not-allowed');
            }
        } else {
            alert('Please enter a valid URL.');
        }
    });

    // Download audio
    downloadAudioBtn.addEventListener('click', (e) => {
        e.preventDefault();

        const url = urlInput.value.trim();

        if (url) {
            // Display initial status message
            popUpContainer.classList.remove('hide')
            statusMessage.textContent = 'Processing request...';
            statusMessage.className = 'message info';
            statusMessage.style.display = 'block';
            progressBar.style.display = 'block';
            
            // Reset progress bar
            progressFill.style.width = '0%';
            progressFill.textContent = '';
            
            const FILE = 'Audio'
            // Emit the request to the backend
            socket.emit('download_request', { url: url, file: FILE});
            
            // Disable the button to prevent multiple requests
            downloadVideoBtn.disabled = true;
            if(downloadVideoBtn.disabled == true){
                downloadVideoBtn.classList.remove('bg-gray-900');
                downloadVideoBtn.classList.add('bg-gray-400');
                downloadVideoBtn.classList.remove('cursor-pointer');
                downloadVideoBtn.classList.remove('hover:bg-gray-800');
                downloadVideoBtn.classList.add('cursor-not-allowed');
            }
        } else {
            alert('Please enter a valid URL.');
        }
    });

    // Listen for progress updates from the server
    socket.on('progress', (data) => {
        if (data.status === 'downloading') {
            const percent = data.percent;
            const speed = data.speed;
            
            progressFill.style.width = percent;
            progressFill.textContent = percent;
            
            statusMessage.textContent = `Downloading...    | Speed: ${speed}`;
            statusMessage.className = 'message info';
            statusMessage.style.display = 'block';

        } else if (data.status === 'finished') {
            progressFill.style.width = '100%';
            progressFill.textContent = '100%';
            statusMessage.textContent = `Download complete!`;
            statusMessage.className = 'message success';
            statusMessage.style.display = 'block';
            // enable the close pop up button
            closeProgressBtn.classList.remove('hide');

            // close the popup progress
            closeProgressBtn.addEventListener('click', (e) => {
                e.preventDefault()
                popUpContainer.classList.add('hide');
            });
            
            downloadVideoBtn.disabled = false; // Re-enable button
            if(downloadVideoBtn.disabled == false){
                downloadVideoBtn.classList.add('bg-gray-900');
                downloadVideoBtn.classList.remove('bg-gray-400');
                downloadVideoBtn.classList.add('cursor-pointer');
                downloadVideoBtn.classList.add('hover:bg-gray-800');
                downloadVideoBtn.classList.remove('cursor-not-allowed');
            }
        } else if (data.status === 'error') {
            progressBar.style.display = 'none';
            statusMessage.textContent = data.message;
            statusMessage.className = 'message error';
            statusMessage.style.display = 'block';
            closeProgressBtn.classList.remove('hide');
            downloadVideoBtn.disabled = false; // Re-enable button
            if(downloadVideoBtn.disabled == false){
                downloadVideoBtn.classList.add('bg-gray-900');
                downloadVideoBtn.classList.remove('bg-gray-400');
                downloadVideoBtn.classList.add('cursor-pointer');
                downloadVideoBtn.classList.add('hover:bg-gray-800');
                downloadVideoBtn.classList.remove('cursor-not-allowed');
            }
        }
    });

    socket.on('connect', () => {
        console.log('Connected to server via SocketIO');
    });
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
})