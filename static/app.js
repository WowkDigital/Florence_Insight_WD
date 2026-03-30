document.addEventListener('DOMContentLoaded', () => {
    // Initialize icons
    lucide.createIcons();

    // Elements
    const uploadTrigger = document.getElementById('upload-trigger');
    const uploadOverlay = document.getElementById('upload-overlay');
    const closeModal = document.getElementById('close-modal');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const fileName = document.getElementById('file-name');
    const analyzeBtn = document.getElementById('analyze-btn');
    const statusArea = document.getElementById('status-area');
    const gallery = document.getElementById('gallery');
    const searchInput = document.getElementById('search-input');
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notification-text');

    let allRecords = [];
    let isPolling = false;

    // Functions
    const showNotification = (message, isError = false) => {
        notificationText.textContent = message;
        notification.classList.remove('hidden');
        notification.style.borderColor = isError ? '#f85149' : 'var(--accent-color)';
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 5000);
    };

    const fetchGallery = async (silent = false) => {
        try {
            const response = await fetch('/images');
            const records = await response.json();
            
            // Only re-render if data actually changed to avoid flickering
            if (JSON.stringify(records) !== JSON.stringify(allRecords)) {
                allRecords = records;
                renderGallery(allRecords);
            }

            // Check if we need to continue polling
            const hasPending = allRecords.some(r => r.status === 'pending');
            if (hasPending && !isPolling) {
                startPolling();
            } else if (!hasPending && isPolling) {
                stopPolling();
            }
        } catch (error) {
            console.error('Error fetching gallery:', error);
            if (!silent) showNotification('Failed to load gallery.', true);
        }
    };

    const startPolling = () => {
        if (isPolling) return;
        isPolling = true;
        console.log("Starting background polling...");
        const pollInterval = setInterval(async () => {
            if (!isPolling) {
                clearInterval(pollInterval);
                return;
            }
            await fetchGallery(true);
        }, 3000);
    };

    const stopPolling = () => {
        isPolling = false;
        console.log("Stopped background polling.");
    };

    const renderGallery = (records) => {
        if (records.length === 0) {
            gallery.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="image"></i>
                    <p>No images imported yet. Start by adding a new image.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        gallery.innerHTML = records.map(record => {
            const isPending = record.status === 'pending';
            const isError = record.status === 'error';
            
            return `
                <div class="image-card ${isPending ? 'pending' : ''}">
                    <div class="card-img-container">
                        <img src="/uploads/${record.image_path}" alt="${record.filename}">
                        ${isPending ? '<div class="card-loader"><div class="mini-loader"></div></div>' : ''}
                    </div>
                    <div class="card-content">
                        <h3>${record.filename}</h3>
                        <div class="description-container">
                            ${isPending ? '<p class="status-text blink">AI is thinking...</p>' : 
                              isError ? `<p class="status-text error">Error during analysis</p>` :
                              `<p>${record.description}</p>`}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    };

    let selectedFiles = [];

    const updateFileListUI = () => {
        const container = document.getElementById('file-list-container');
        const list = document.getElementById('file-list');
        
        if (selectedFiles.length > 0) {
            container.classList.remove('hidden');
            list.innerHTML = selectedFiles.map((file, index) => `
                <div class="file-item" id="file-item-${index}">
                    <span>${file.name}</span>
                    <span class="file-status pending">Pending</span>
                </div>
            `).join('');
        } else {
            container.classList.add('hidden');
        }
    };

    const handleFilesSelect = (files) => {
        selectedFiles = Array.from(files).filter(f => f.type.startsWith('image/'));
        
        if (selectedFiles.length === 0) {
            showNotification('Please select valid image files.', true);
            return;
        }

        updateFileListUI();
        dropZone.classList.add('hidden');
        previewArea.classList.remove('hidden');

        // Show first file preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            fileName.textContent = selectedFiles.length === 1 ? selectedFiles[0].name : `${selectedFiles.length} files selected`;
        };
        reader.readAsDataURL(selectedFiles[0]);
    };

    // Event Listeners
    uploadTrigger.addEventListener('click', () => {
        uploadOverlay.classList.remove('hidden');
        previewArea.classList.add('hidden');
        dropZone.classList.remove('hidden');
        statusArea.classList.add('hidden');
        document.getElementById('file-list-container').classList.add('hidden');
        fileInput.value = '';
        selectedFiles = [];
    });

    closeModal.addEventListener('click', () => {
        uploadOverlay.classList.add('hidden');
    });

    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent-color)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border-color)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-color)';
        handleFilesSelect(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFilesSelect(e.target.files);
    });

    // Analysis Settings Elements
    const tokensSlider = document.getElementById('tokens-slider');
    const tokensVal = document.getElementById('tokens-val');
    const beamsSlider = document.getElementById('beams-slider');
    const beamsVal = document.getElementById('beams-val');
    const presetBtns = document.querySelectorAll('.preset-btn');

    let currentPrompt = '<DETAILED_CAPTION>';

    tokensSlider.addEventListener('input', (e) => {
        tokensVal.textContent = e.target.value;
        presetBtns.forEach(b => b.classList.remove('active'));
    });

    beamsSlider.addEventListener('input', (e) => {
        beamsVal.textContent = e.target.value;
        presetBtns.forEach(b => b.classList.remove('active'));
    });

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            presetBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPrompt = btn.getAttribute('data-prompt');
            tokensSlider.value = btn.getAttribute('data-tokens');
            tokensVal.textContent = tokensSlider.value;
            beamsSlider.value = btn.getAttribute('data-beams');
            beamsVal.textContent = beamsSlider.value;
        });
    });

    const processQueue = async () => {
        if (selectedFiles.length === 0) return;

        const total = selectedFiles.length;
        previewArea.classList.add('hidden');
        statusArea.classList.remove('hidden');
        
        const loaderText = statusArea.querySelector('p');

        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            const item = document.getElementById(`file-item-${i}`);
            const status = item.querySelector('.file-status');

            loaderText.textContent = `Queuing image ${i + 1} of ${total}...`;
            status.textContent = 'Queuing...';
            status.className = 'file-status processing';

            const formData = new FormData();
            formData.append('image', file);
            formData.append('prompt', currentPrompt);
            formData.append('max_tokens', tokensSlider.value);
            formData.append('beams', beamsSlider.value);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                if (result.success) {
                    status.textContent = 'Enqueued';
                    status.className = 'file-status done';
                } else {
                    status.textContent = 'Error';
                    status.className = 'file-status error';
                }
            } catch (error) {
                status.textContent = 'Failed';
                status.className = 'file-status error';
            }
        }

        loaderText.textContent = 'Batch enqueued! Processing in background...';
        showNotification(`${total} images added to background queue.`);
        
        // Final refresh and close
        fetchGallery();
        setTimeout(() => {
            uploadOverlay.classList.add('hidden');
        }, 1200);
    };

    analyzeBtn.addEventListener('click', processQueue);

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allRecords.filter(record => 
            record.description.toLowerCase().includes(query) || 
            record.filename.toLowerCase().includes(query)
        );
        renderGallery(filtered);
    });

    fetchGallery();
});
