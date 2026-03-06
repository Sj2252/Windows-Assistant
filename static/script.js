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
const appsContainer = document.getElementById('apps-container');

shutdownBtn.onclick = () => {
    if (confirm("Stop the assistant program?")) {
        // Change orb to white first
        updateState('stopping');

        // Wait a bit before sending shutdown request
        setTimeout(() => {
            fetch('/shutdown', { method: 'POST' })
                .then(() => {
                    document.body.classList.add('stopped');
                    if (statusBadge) {
                        statusBadge.textContent = 'Assistant Stopped';
                        statusBadge.className = 'status-badge disconnected';
                    }
                    updateState('dormant');
                    alert("Assistant is shutting down. This tab will now close.");

                    // Wait for alert to be dismissed then try to close
                    setTimeout(() => {
                        window.open('', '_self', '').close();
                    }, 500);
                })
                .catch(() => alert("Could not stop assistant. Check if it is already closed."));
        }, 1500); // 1.5 second delay to show white orb
    }
};

manualBtn.onclick = () => {
    fetchApps();
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

async function fetchApps() {
    try {
        const response = await fetch('/apps');
        const data = await response.json();
        renderApps(data.apps);
    } catch (error) {
        console.error('Error fetching apps:', error);
    }
}

function renderApps(apps) {
    appsContainer.innerHTML = '';
    // Unique apps list (some are aliases in config)
    const uniqueApps = [...new Set(apps)];
    uniqueApps.sort().forEach(app => {
        const pill = document.createElement('div');
        pill.className = 'app-pill';
        pill.textContent = app;
        pill.title = `Say "Iris, open ${app}"`;
        appsContainer.appendChild(pill);
    });
}

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

// Visualizer setup
const canvas = document.getElementById('visualizer-canvas');
const ctx = canvas.getContext('2d');
let audioContext, analyser, dataArray, source;
let isVisualizing = false;

function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

async function initVisualizer() {
    if (isVisualizing) return;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        isVisualizing = true;
        animate();
    } catch (err) {
        console.error("Mic access denied or error:", err);
    }
}

function animate() {
    if (!isVisualizing) return;
    requestAnimationFrame(animate);

    analyser.getByteFrequencyData(dataArray);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 85; // slightly larger than the orb
    const bars = 60;
    const barWidth = 3;

    for (let i = 0; i < bars; i++) {
        const rads = (Math.PI * 2) / bars;
        const barHeight = dataArray[i] * 0.5;

        const x = centerX + Math.cos(rads * i) * radius;
        const y = centerY + Math.sin(rads * i) * radius;
        const x_end = centerX + Math.cos(rads * i) * (radius + barHeight);
        const y_end = centerY + Math.sin(rads * i) * (radius + barHeight);

        // Color based on index and intensity
        const hue = (i / bars) * 360;
        ctx.strokeStyle = `hsla(${hue}, 100%, 50%, ${dataArray[i] / 255})`;
        ctx.lineWidth = barWidth;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x_end, y_end);
        ctx.stroke();
    }

    // Subtle glow on the orb based on average volume
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    orb.style.transform = `scale(${1 + (average / 500)})`;
}

// Start visualizer on first interaction
window.addEventListener('mousedown', () => {
    initVisualizer();
    if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume();
    }
}, { once: false });

function updateState(state) {
    stateLabel.textContent = state;
    orb.className = 'orb ' + state;

    if (state === 'dormant') {
        lastCommandText.textContent = 'Say "Arise" to wake me up';
    } else if (state === 'active') {
        lastCommandText.textContent = 'Waiting for "Iris"...';
    } else if (state === 'listening') {
        lastCommandText.textContent = 'Listening...';
    } else if (state === 'stopping') {
        lastCommandText.textContent = 'Shutting down...';
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

connect();
