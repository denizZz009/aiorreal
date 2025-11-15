// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Global state
let selectedFiles = [];

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const selectedFilesSection = document.getElementById('selectedFiles');
const fileList = document.getElementById('fileList');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const fastModeCheckbox = document.getElementById('fastMode');
const apiStatusElement = document.getElementById('apiStatus');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    setupEventListeners();
});

// Check API Status
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/health`);
        if (response.ok) {
            apiStatusElement.textContent = '🟢 Online';
            apiStatusElement.classList.add('online');
            apiStatusElement.classList.remove('offline');
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        apiStatusElement.textContent = '🔴 Offline';
        apiStatusElement.classList.add('offline');
        apiStatusElement.classList.remove('online');
        console.error('API Status Error:', error);
        
        // Show warning banner
        showAPIWarning();
    }
}

// Show API Warning Banner
function showAPIWarning() {
    const existingWarning = document.getElementById('apiWarning');
    if (existingWarning) return;
    
    const warning = document.createElement('div');
    warning.id = 'apiWarning';
    warning.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        text-align: center;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideDown 0.3s ease;
    `;
    warning.innerHTML = `
        <strong>⚠️ API Sunucusu Çalışmıyor</strong><br>
        <span style="font-size: 0.9rem;">Lütfen terminalde <code style="background: rgba(0,0,0,0.2); padding: 0.2rem 0.5rem; border-radius: 0.25rem;">python run_server.py</code> komutunu çalıştırın</span>
    `;
    document.body.prepend(warning);
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
}

// Setup Event Listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = Array.from(e.dataTransfer.files);
        addFiles(files);
    });

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeFiles);
}

// Handle File Select
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

// Add Files
function addFiles(files) {
    // Filter valid files
    const validExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.avi'];
    const validFiles = files.filter(file => {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        return validExtensions.includes(ext);
    });

    if (validFiles.length === 0) {
        alert('Lütfen geçerli bir dosya formatı seçin (JPG, PNG, WEBP, MP4, MOV, AVI)');
        return;
    }

    // Add to selected files (max 10)
    validFiles.forEach(file => {
        if (selectedFiles.length < 10) {
            selectedFiles.push(file);
        }
    });

    if (selectedFiles.length > 10) {
        selectedFiles = selectedFiles.slice(0, 10);
        alert('Maksimum 10 dosya seçebilirsiniz');
    }

    updateFileList();
    analyzeBtn.disabled = false;
}

// Update File List Display
function updateFileList() {
    if (selectedFiles.length === 0) {
        selectedFilesSection.style.display = 'none';
        analyzeBtn.disabled = true;
        return;
    }

    selectedFilesSection.style.display = 'block';
    fileList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const isVideo = file.type.startsWith('video/');
        const icon = isVideo ? '🎥' : '🖼️';
        const sizeKB = (file.size / 1024).toFixed(2);

        fileItem.innerHTML = `
            <div class="file-info">
                <span class="file-icon">${icon}</span>
                <div>
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${sizeKB} KB</div>
                </div>
            </div>
            <button class="btn-remove" onclick="removeFile(${index})">Kaldır</button>
        `;

        fileList.appendChild(fileItem);
    });
}

// Remove File
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
}

// Analyze Files
async function analyzeFiles() {
    if (selectedFiles.length === 0) return;

    // Show loading state
    analyzeBtn.disabled = true;
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';

    // Clear previous results
    resultsContainer.innerHTML = '';
    resultsSection.style.display = 'block';

    const fastMode = fastModeCheckbox.checked;

    try {
        if (selectedFiles.length === 1) {
            // Single file analysis
            const result = await analyzeSingleFile(selectedFiles[0], fastMode);
            displayResult(result);
        } else {
            // Batch analysis
            const results = await analyzeBatchFiles(selectedFiles);
            results.forEach(result => displayResult(result));
        }
    } catch (error) {
        console.error('Analysis Error:', error);
        resultsContainer.innerHTML = `
            <div class="result-card">
                <div class="verdict-badge verdict-high">❌ Hata</div>
                <p>Analiz sırasında bir hata oluştu: ${error.message}</p>
                <p style="color: var(--text-muted); margin-top: 1rem;">
                    API sunucusunun çalıştığından emin olun: <code>python run_server.py</code>
                </p>
            </div>
        `;
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

// Analyze Single File
async function analyzeSingleFile(file, fastMode) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fast_mode', fastMode);

    const response = await fetch(`${API_BASE_URL}/api/v1/detect`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
    }

    return await response.json();
}

// Analyze Batch Files
async function analyzeBatchFiles(files) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/detect/batch`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Batch analysis failed');
    }

    const data = await response.json();
    return data.results;
}

// Display Result
function displayResult(result) {
    const resultCard = document.createElement('div');
    resultCard.className = 'result-card';

    // Get verdict display based on confidence
    const verdictDisplay = getVerdictDisplay(result.confidence);
    const verdictClass = verdictDisplay.class;
    const verdictText = verdictDisplay.text;
    const verdictIcon = verdictDisplay.icon;

    // Build scores HTML
    let scoresHTML = '';
    if (result.scores && Object.keys(result.scores).length > 0) {
        scoresHTML = '<div class="score-info">';
        for (const [key, value] of Object.entries(result.scores)) {
            const label = formatScoreLabel(key);
            scoresHTML += `
                <div class="score-item">
                    <div class="score-label">${label}</div>
                    <div class="score-value">${value}</div>
                </div>
            `;
        }
        scoresHTML += '</div>';
    }

    // Build evidence HTML
    let evidenceHTML = '';
    if (result.evidence && result.evidence.length > 0) {
        evidenceHTML = `
            <div class="evidence-section">
                <h4>Tespit Edilen Kanıtlar:</h4>
                <ul class="evidence-list">
                    ${result.evidence.map(e => `<li>${e}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    resultCard.innerHTML = `
        <div class="result-header">
            <div class="result-filename">${result.filename || 'File'}</div>
            <div class="result-time">${result.processing_time_ms || 0} ms</div>
        </div>

        <div class="verdict-badge ${verdictClass}">
            ${verdictIcon} ${verdictText}
        </div>

        <div class="confidence-bar">
            <div class="confidence-label">
                <span>Confidence Score</span>
                <span>${(result.confidence * 100).toFixed(1)}%</span>
            </div>
            <div class="confidence-progress">
                <div class="confidence-fill" style="width: ${result.confidence * 100}%"></div>
            </div>
        </div>

        <div class="score-info">
            <div class="score-item">
                <div class="score-label">Total Score</div>
                <div class="score-value">${result.total_score || 0}</div>
            </div>
            ${result.frames_analyzed ? `
                <div class="score-item">
                    <div class="score-label">Frames Analyzed</div>
                    <div class="score-value">${result.frames_analyzed}</div>
                </div>
            ` : ''}
        </div>

        ${scoresHTML}
        ${evidenceHTML}
    `;

    resultsContainer.appendChild(resultCard);
}

// Format Score Label
function formatScoreLabel(key) {
    const labels = {
        'watermark_detected': 'Watermark Tespit',
        'c2pa_synthetic': 'C2PA Synthetic',
        'metadata_suspicious': 'Şüpheli Metadata',
        'checkboard_pattern': 'Checkerboard Pattern',
        'freq_ratio_anomaly': 'Frekans Anomalisi',
        'temporal_flicker': 'Temporal Flicker',
        'noise_variance_low': 'Düşük Gürültü',
        'motion_vector_irregular': 'Düzensiz Hareket',
        'rgb_correlation_high': 'Yüksek RGB Korelasyon',
        'edge_fragmented': 'Parçalı Kenarlar'
    };
    return labels[key] || key;
}

// Get Verdict Icon and Class based on confidence
function getVerdictDisplay(confidence) {
    if (confidence >= 0.70) {
        return { icon: '🚨', text: 'AI-Generated', class: 'verdict-high' };
    } else if (confidence >= 0.50) {
        return { icon: '⚠️', text: 'Likely AI-Generated', class: 'verdict-medium' };
    } else if (confidence >= 0.30) {
        return { icon: '🤔', text: 'Suspicious', class: 'verdict-suspicious' };
    } else {
        return { icon: '✅', text: 'Likely Real', class: 'verdict-real' };
    }
}
