// settings page - still learning this
// TODO: make the form work better, fix validation

// when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentSettings();
    
    // form submission
    const form = document.getElementById('settings-form');
    form.addEventListener('submit', handleFormSubmit);
});

// load current settings - simple version
async function loadCurrentSettings() {
    try {
        const response = await fetch('http://127.0.0.1:5000/settings');
        const data = await response.json();
        
        // load name
        if (data.name) {
            document.getElementById('name').value = data.name;
        }
        
        // load time settings
        if (data.preferred_hour) {
            document.getElementById('hour').value = data.preferred_hour;
        }
        if (data.preferred_minute) {
            document.getElementById('minute').value = data.preferred_minute;
        }
        if (data.preferred_am_pm) {
            document.getElementById('am_pm').value = data.preferred_am_pm;
        }
        
        // load skater preference
        if (data.is_skater) {
            document.getElementById('is_skater').checked = data.is_skater;
        }
        
        // load difficulty
        if (data.difficulty) {
            const radioButton = document.getElementById(data.difficulty);
            if (radioButton) {
                radioButton.checked = true;
            }
        }
    } catch (error) {
        console.log('Error loading settings:', error);
        showStatusMessage('Error loading settings', 'error');
    }
}

// handle form submission - kept it simple
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const settings = {
        name: formData.get('name'),
        preferred_hour: formData.get('hour'),
        preferred_minute: formData.get('minute'),
        preferred_am_pm: formData.get('am_pm'),
        is_skater: formData.get('is_skater') === 'on',
        difficulty: formData.get('difficulty')
    };
    
    // basic validation
    if (!settings.name) {
        showStatusMessage('Please enter your name', 'error');
        return;
    }
    
    if (!settings.preferred_hour || !settings.preferred_minute || !settings.preferred_am_pm) {
        showStatusMessage('Please select your preferred time', 'error');
        return;
    }
    
    if (!settings.difficulty) {
        showStatusMessage('Please select a difficulty level', 'error');
        return;
    }
    
    // Just show success message - no backend call
    showStatusMessage('Settings saved! (Demo mode)', 'success');
}

// show status message - basic version
function showStatusMessage(message, type) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.className = 'status-message ' + type;
    
    // clear after 3 seconds
    setTimeout(function() {
        statusDiv.textContent = '';
        statusDiv.className = 'status-message';
    }, 3000);
}