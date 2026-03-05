const statusBadge = document.getElementById('connection-status');
const orb = document.getElementById('visualizer-orb');
const stateLabel = document.getElementById('current-state');
const lastCommandText = document.getElementById('last-command');
const historyFeed = document.getElementById('history-feed');
const volumeFill = document.querySelector('#volume-indicator .progress-fill');
const brightnessFill = document.querySelector('#brightness-indicator .progress-fill');
const shutdownBtn = document.getElementById('shutdown-btn');
const manualBtn = document.getElementById('manual-btn');
const manualModal = document.getElementById('manual-modal');
const closeManual = document.getElementById('close-manual');

shutdownBtn.onclick = () => {
    if (confirm("Stop the assistant program?")) {
        fetch('/shutdown', { method: 'POST' })
            .then(() => alert("Assistant has been stopped."))
            .catch(() => alert("Could not stop assistant. Check if it is already closed."));
    }
};

manualBtn.onclick = () => {
    manualModal.classList.add('active');
};

closeManual.onclick = () => {
    manualModal.classList.remove('active');
};

window.onclick = (event) => {
    if (event.target === manualModal) {
        manualModal.classList.remove('active');
    }
};

function connect() {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
        statusBadge.textContent = 'Connected';
        statusBadge.classList.remove('disconnected');
        statusBadge.classList.add('connected');
        console.log('Connected to assistant');
    };

    ws.onclose = () => {
        statusBadge.textContent = 'Disconnected';
        statusBadge.classList.remove('connected');
        statusBadge.classList.add('disconnected');
        console.log('Disconnected. Retrying in 2s...');
        setTimeout(connect, 2000);
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        const { type, data } = message;

        switch (type) {
            case 'state':
                updateState(data);
                break;
            case 'transcript':
                updateTranscript(data);
                break;
            case 'volume':
                updateVolume(data);
                break;
            case 'brightness':
                updateBrightness(data);
                break;
        }
    };
}

connect();

function updateState(state) {
    stateLabel.textContent = state;
    orb.className = 'orb ' + state;

    if (state === 'dormant') {
        lastCommandText.textContent = 'Say "Arise" to wake me up';
    } else if (state === 'active') {
        lastCommandText.textContent = 'Waiting for "Iris"...';
    } else if (state === 'listening') {
        lastCommandText.textContent = 'Listening...';
    }
}

function updateTranscript(text) {
    if (!text) return;

    lastCommandText.textContent = text;

    // Add to history
    const item = document.createElement('div');
    item.className = 'history-item';
    item.textContent = text;
    historyFeed.prepend(item);

    // Check for volume/brightness updates in text to update UI immediately
    const volumeMatch = text.match(/volume (?:to )?(\d+)/i);
    if (volumeMatch) updateVolume(volumeMatch[1]);

    const brightnessMatch = text.match(/brightness (?:to )?(\d+)/i);
    if (brightnessMatch) updateBrightness(brightnessMatch[1]);
}

function updateVolume(value) {
    volumeFill.style.width = value + '%';
}

function updateBrightness(value) {
    brightnessFill.style.width = value + '%';
}
