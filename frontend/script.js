// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const processBtn = document.getElementById('processBtn');
const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const transcriptContainer = document.getElementById('transcriptContainer');
const downloadBtn = document.getElementById('downloadBtn');
const newFileBtn = document.getElementById('newFileBtn');

// Recording Elements
const uploadModeBtn = document.getElementById('uploadModeBtn');
const recordModeBtn = document.getElementById('recordModeBtn');
const recordArea = document.getElementById('recordArea');
const micIcon = document.getElementById('micIcon');
const recordWaves = document.getElementById('recordWaves');
const recordStatus = document.getElementById('recordStatus');
const recordTimer = document.getElementById('recordTimer');
const startRecordBtn = document.getElementById('startRecordBtn');
const stopRecordBtn = document.getElementById('stopRecordBtn');
const playRecordBtn = document.getElementById('playRecordBtn');

// State
let selectedFile = null;
let currentTranscript = null;
let processingInterval = null;
let currentMode = 'upload';
let mediaRecorder = null;
let recordedChunks = [];
let recordingStartTime = null;
let recordingTimer = null;
let audioContext = null;
let analyser = null;
let microphone = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkMicrophoneSupport();
});

// Check microphone support
function checkMicrophoneSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        recordModeBtn.disabled = true;
        recordModeBtn.title = 'Microphone recording is not supported in this browser';
        recordModeBtn.style.opacity = '0.5';
    }
}

function setupEventListeners() {
    // Mode selector
    uploadModeBtn.addEventListener('click', () => switchMode('upload'));
    recordModeBtn.addEventListener('click', () => switchMode('record'));
    
    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input
    fileInput.addEventListener('change', handleFileSelect);
    
    // Remove file
    removeFile.addEventListener('click', clearFile);
    
    // Recording controls
    startRecordBtn.addEventListener('click', startRecording);
    stopRecordBtn.addEventListener('click', stopRecording);
    playRecordBtn.addEventListener('click', playRecording);
    
    // Process button
    processBtn.addEventListener('click', startProcessing);
    
    // Action buttons
    downloadBtn.addEventListener('click', downloadTranscript);
    newFileBtn.addEventListener('click', resetToUpload);
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File selection handler
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// File handling
function handleFile(file) {
    // Validate file type (more lenient for recorded files)
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/m4a', 'audio/flac', 'audio/ogg', 'audio/webm'];
    const isValidType = validTypes.includes(file.type) || file.name.match(/\.(mp3|wav|m4a|flac|ogg|webm)$/i);
    
    if (!isValidType && !file.name.startsWith('recording-')) {
        showError('Please select a valid audio file (MP3, WAV, M4A, FLAC, OGG)');
        return;
    }
    
    // Check file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
        showError('File size must be less than 100MB');
        return;
    }
    
    selectedFile = file;
    displayFileInfo(file);
    processBtn.disabled = false;
}

function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
}

function clearFile() {
    selectedFile = null;
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    fileInput.value = '';
    processBtn.disabled = true;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Processing
async function startProcessing() {
    if (!selectedFile) return;
    // Guard against double-clicks
    processBtn.disabled = true;
    const btnText = processBtn.querySelector('.btn-text');
    const btnLoader = processBtn.querySelector('.btn-loader');
    if (btnText && btnLoader) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
    }
    
    // Get options
    const options = {
        whisper_model: document.getElementById('whisperModel').value,
        language: document.getElementById('language').value,
        device: document.getElementById('device').value,
        stemming: document.getElementById('stemming').checked
    };
    
    // Show processing section
    uploadSection.style.display = 'none';
    processingSection.style.display = 'block';
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('audio', selectedFile);
        formData.append('options', JSON.stringify(options));
        
        // Upload and start processing
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            const errText = await uploadResponse.text();
            throw new Error(`Upload failed: ${errText}`);
        }
        
        const { job_id } = await uploadResponse.json();
        
        // Poll for progress
        await pollProgress(job_id);
        
        // Get results
        const resultResponse = await fetch(`/api/result/${job_id}`);
        if (!resultResponse.ok) {
            const errText = await resultResponse.text();
            throw new Error(`Failed to get results: ${errText}`);
        }
        
        const transcript = await resultResponse.json();
        currentTranscript = transcript;
        
        // Show results
        showResults();
        
    } catch (error) {
        console.error('Processing error:', error);
        showError(error?.message || 'An error occurred during processing. Please try again.');
        resetToUpload();
    } finally {
        // Restore button state
        if (btnText && btnLoader) {
            btnText.style.display = '';
            btnLoader.style.display = 'none';
        }
        processBtn.disabled = false;
    }
}

function startProcessingAnimation() {
    let progress = 0;
    let step = 1;
    const steps = ['Initializing...', 'Audio preprocessing...', 'Speech transcription...', 'Speaker diarization...', 'Final processing...'];
    
    progressText.textContent = steps[0];
    
    processingInterval = setInterval(() => {
        progress += Math.random() * 15;
        
        if (progress > 100) progress = 100;
        
        progressFill.style.width = progress + '%';
        
        // Update current step
        const currentStep = Math.min(Math.floor(progress / 20) + 1, 5);
        if (currentStep !== step) {
            // Mark previous step as completed
            if (step <= 4) {
                const prevStepEl = document.getElementById(`step${step}`);
                if (prevStepEl) {
                    prevStepEl.classList.remove('active');
                    prevStepEl.classList.add('completed');
                }
            }
            
            step = currentStep;
            if (step <= 4) {
                progressText.textContent = steps[step];
                const stepEl = document.getElementById(`step${step}`);
                if (stepEl) {
                    stepEl.classList.add('active');
                }
            }
        }
        
        if (progress >= 100) {
            clearInterval(processingInterval);
            progressText.textContent = 'Processing complete!';
            
            // Mark final step as completed
            const finalStep = document.getElementById('step4');
            if (finalStep) {
                finalStep.classList.remove('active');
                finalStep.classList.add('completed');
            }
        }
    }, 200);
}

// Poll for processing progress
async function pollProgress(jobId) {
    return new Promise((resolve, reject) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${jobId}`);
                if (!response.ok) {
                    throw new Error('Failed to get status');
                }
                
                const status = await response.json();
                
                // Update progress UI
                updateProgressUI(status);
                
                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    resolve();
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    reject(new Error(status.error || 'Processing failed'));
                }
                
            } catch (error) {
                clearInterval(pollInterval);
                reject(error);
            }
        }, 1000); // Poll every second
    });
}

function updateProgressUI(status) {
    const progress = status.progress || 0;
    const step = status.step || 'Processing...';
    
    progressFill.style.width = progress + '%';
    progressText.textContent = step;
    
    // Update step indicators
    const currentStepNum = Math.min(Math.floor(progress / 25) + 1, 4);
    
    for (let i = 1; i <= 4; i++) {
        const stepEl = document.getElementById(`step${i}`);
        if (!stepEl) continue;
        
        stepEl.classList.remove('active', 'completed');
        
        if (i < currentStepNum) {
            stepEl.classList.add('completed');
        } else if (i === currentStepNum) {
            stepEl.classList.add('active');
        }
    }
}

function showResults() {
    // Hide processing, show results
    processingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Display transcript
    displayTranscript(currentTranscript);
}

function generateSampleTranscript() {
    return [
        {
            speaker: 'Speaker 1',
            startTime: '00:00:00',
            endTime: '00:00:15',
            text: 'Welcome to our quarterly business review meeting. Today we\'ll be discussing our progress over the past three months and outlining our goals for the upcoming quarter.'
        },
        {
            speaker: 'Speaker 2',
            startTime: '00:00:16',
            endTime: '00:00:28',
            text: 'Thank you, John. I\'d like to start by presenting our sales figures. We\'ve seen a 23% increase in revenue compared to the same period last year, which is fantastic news.'
        },
        {
            speaker: 'Speaker 1',
            startTime: '00:00:29',
            endTime: '00:00:42',
            text: 'That\'s excellent, Sarah. Can you break down which product lines contributed most to this growth? I\'m particularly interested in how our new AI features performed in the market.'
        },
        {
            speaker: 'Speaker 3',
            startTime: '00:00:43',
            endTime: '00:00:58',
            text: 'I can answer that. The AI-powered analytics dashboard has been our top performer, accounting for 40% of the total revenue increase. Customer feedback has been overwhelmingly positive.'
        }
    ];
}

function displayTranscript(transcript) {
    transcriptContainer.innerHTML = '';
    
    transcript.forEach((segment, index) => {
        const segmentEl = document.createElement('div');
        segmentEl.className = 'speaker-segment';
        segmentEl.style.animationDelay = `${index * 0.1}s`;
        
        segmentEl.innerHTML = `
            <div class="speaker-label">
                ${segment.speaker}
                <span class="timestamp">${segment.startTime} - ${segment.endTime}</span>
            </div>
            <div class="speaker-text">${segment.text}</div>
        `;
        
        transcriptContainer.appendChild(segmentEl);
    });
}

// Download functionality
function downloadTranscript() {
    if (!currentTranscript) return;
    
    let content = `Whisper Diarization Transcript\n`;
    content += `Generated: ${new Date().toLocaleString()}\n`;
    content += `File: ${selectedFile?.name || 'Unknown'}\n\n`;
    content += `${'='.repeat(50)}\n\n`;
    
    currentTranscript.forEach((segment) => {
        content += `[${segment.startTime} - ${segment.endTime}] ${segment.speaker}:\n`;
        content += `${segment.text}\n\n`;
    });
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript-${selectedFile?.name || 'audio'}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Mode switching
function switchMode(mode) {
    currentMode = mode;
    
    // Update buttons
    uploadModeBtn.classList.toggle('active', mode === 'upload');
    recordModeBtn.classList.toggle('active', mode === 'record');
    
    // Show/hide areas
    if (mode === 'upload') {
        uploadArea.style.display = 'block';
        recordArea.style.display = 'none';
    } else {
        uploadArea.style.display = 'none';
        recordArea.style.display = 'block';
    }
    
    // Clear current selection
    clearFile();
    clearRecording();
}

// Recording functions
async function startRecording() {
    try {
        // Request microphone permission
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            } 
        });
        
        // Setup MediaRecorder
        recordedChunks = [];
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
            const audioFile = new File([audioBlob], `recording-${Date.now()}.wav`, { type: 'audio/wav' });
            handleFile(audioFile);
            
            // Show play button
            playRecordBtn.style.display = 'flex';
        };
        
        // Setup audio visualization
        setupAudioVisualization(stream);
        
        // Start recording
        mediaRecorder.start(100); // Record in 100ms chunks
        recordingStartTime = Date.now();
        
        // Update UI
        updateRecordingUI(true);
        startRecordingTimer();
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showError('Could not access microphone. Please check permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        
        // Stop all tracks to release microphone
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Update UI
        updateRecordingUI(false);
        stopRecordingTimer();
        
        // Clean up audio context
        if (audioContext) {
            audioContext.close();
            audioContext = null;
        }
    }
}

function playRecording() {
    if (selectedFile) {
        const audioUrl = URL.createObjectURL(selectedFile);
        const audio = new Audio(audioUrl);
        
        audio.play().catch(error => {
            console.error('Error playing audio:', error);
            showError('Could not play the recorded audio.');
        });
        
        // Clean up URL after playing
        audio.addEventListener('ended', () => {
            URL.revokeObjectURL(audioUrl);
        });
    }
}

function setupAudioVisualization(stream) {
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    microphone = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 256;
    microphone.connect(analyser);
    
    // Start visualization
    visualizeAudio();
}

function visualizeAudio() {
    if (!analyser) return;
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);
    
    // Calculate average volume
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    const normalizedVolume = average / 255;
    
    // Update wave heights based on volume
    const waves = recordWaves.querySelectorAll('.record-wave');
    waves.forEach((wave, index) => {
        const height = Math.max(10, normalizedVolume * 40 + Math.random() * 10);
        wave.style.height = `${height}px`;
    });
    
    // Continue animation if recording
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        requestAnimationFrame(visualizeAudio);
    }
}

function updateRecordingUI(isRecording) {
    micIcon.classList.toggle('recording', isRecording);
    recordWaves.classList.toggle('active', isRecording);
    
    if (isRecording) {
        recordStatus.querySelector('p').textContent = 'Recording... Click stop when finished';
        startRecordBtn.style.display = 'none';
        stopRecordBtn.style.display = 'flex';
        recordTimer.style.display = 'block';
    } else {
        recordStatus.querySelector('p').textContent = 'Recording completed! You can now process the audio.';
        startRecordBtn.style.display = 'flex';
        stopRecordBtn.style.display = 'none';
        recordTimer.style.display = 'none';
    }
}

function startRecordingTimer() {
    recordingTimer = setInterval(() => {
        const elapsed = Date.now() - recordingStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        recordTimer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopRecordingTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
}

function clearRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        stopRecording();
    }
    
    recordedChunks = [];
    playRecordBtn.style.display = 'none';
    recordTimer.textContent = '00:00';
    recordStatus.querySelector('p').textContent = 'Click the record button to start recording';
    updateRecordingUI(false);
}

// Reset to upload
function resetToUpload() {
    // Reset state
    selectedFile = null;
    currentTranscript = null;
    
    if (processingInterval) {
        clearInterval(processingInterval);
        processingInterval = null;
    }
    
    // Reset UI
    clearFile();
    clearRecording();
    uploadSection.style.display = 'block';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Reset progress
    progressFill.style.width = '0%';
    progressText.textContent = 'Initializing...';
    
    // Reset steps
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) {
            step.classList.remove('active', 'completed');
        }
    }
    
    // Reset to upload mode
    switchMode('upload');
}

// Error handling
function showError(message) {
    // Create error toast
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
        max-width: 400px;
    `;
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

// Add error toast animations to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);