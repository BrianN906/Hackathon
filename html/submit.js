// submit page - still working on this
// TODO: fix the form submission, make it work better

let currentTaskId = null;

// when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentTask();
    
    // form submission
    const form = document.getElementById('completion-form');
    form.addEventListener('submit', handleFormSubmit);
    
    // navigation buttons
    const goBackBtn = document.getElementById('go-back-btn');
    if (goBackBtn) {
        goBackBtn.addEventListener('click', function() {
            window.location.href = 'index.html';
        });
    }
    
    const viewGalleryBtn = document.getElementById('view-gallery-btn');
    if (viewGalleryBtn) {
        viewGalleryBtn.addEventListener('click', function() {
            window.location.href = 'gallery.html';
        });
    }
});

// load current task - simple version
async function loadCurrentTask() {
    try {
        currentTaskId = sessionStorage.getItem('currentTaskId');
        
        if (!currentTaskId) {
            showStatusMessage('No active task found. Go to home page first.', 'error');
            return;
        }
        
        console.log('Current task ID:', currentTaskId);
    } catch (error) {
        console.log('Error loading task:', error);
        showStatusMessage('Error loading task. Check server.', 'error');
    }
}

// handle form submission - had some problems with this
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (!currentTaskId) {
        showStatusMessage('No active task to complete.', 'error');
        return;
    }
    
    const formData = new FormData(event.target);
    const image = formData.get('image');
    const description = formData.get('description');
    
    if (!image || image.size === 0) {
        showStatusMessage('Please select an image.', 'error');
        return;
    }
    
    try {
        // submit to server
        const submitResponse = await fetch('http://127.0.0.1:5000/submit', {
            method: 'POST',
            body: formData
        });
        
        const submitResult = await submitResponse.json();
        
        if (!submitResult.success) {
            showStatusMessage('Error: ' + submitResult.message, 'error');
            return;
        }
        
        showStatusMessage('Task completed and saved!', 'success');
        
        // clear form
        event.target.reset();
        
        // go back to home after 2 seconds
        setTimeout(function() {
            window.location.href = 'index.html';
        }, 2000);
        
    } catch (error) {
        console.log('Error submitting:', error);
        showStatusMessage('Error submitting. Try again.', 'error');
    }
}

// show status message - basic version
function showStatusMessage(message, type) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.className = 'status-message ' + type;
    
    // clear after 5 seconds
    setTimeout(function() {
        statusDiv.textContent = '';
        statusDiv.className = 'status-message';
    }, 5000);
}