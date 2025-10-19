// main page script - still figuring this out

// load user name - took us a while to get this working
async function loadUserName() {
    const userNameElement = document.querySelector('.user-name');
    const welcomeMessage = document.querySelector('.welcome-message');
    if (!userNameElement || !welcomeMessage) return;
    
    try {
        const response = await fetch('/settings');
        const data = await response.json();
        
        if (data.name && data.name.trim()) {
            userNameElement.textContent = data.name;
        } else {
            // hide the username span and change message to just "Welcome back!"
            userNameElement.style.display = 'none';
            welcomeMessage.innerHTML = 'Welcome back!';
        }
    } catch (error) {
        console.log('Error loading name:', error);
        // hide the username span and change message to just "Welcome back!"
        userNameElement.style.display = 'none';
        welcomeMessage.innerHTML = 'Welcome back!';
    }
}

// load daily task
async function loadDailyTask() {
    const taskDisplay = document.getElementById('task-display');
    if (!taskDisplay) return;
    
    try {
        const response = await fetch('/task');
        const data = await response.json();
        
        if (data.task) {
            taskDisplay.textContent = data.task;
            // store task id for later
            if (data.task_id) {
                sessionStorage.setItem('currentTaskId', data.task_id);
            }
        } else {
            taskDisplay.textContent = 'No tasks available';
        }
    } catch (error) {
        console.log('Error loading task:', error);
        taskDisplay.textContent = 'Error loading task. Make sure server is running.';
    }
}

// handle submit button
function handleSubmitClick() {
    window.location.href = 'submit.html';
}

// handle skip day button
async function handleSkipDayClick() {
    try {
        const response = await fetch('/skip-day', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // reload the task display
            await loadDailyTask();
            showStatusMessage('Skipped to next day! New task loaded.', 'success');
        } else {
            showStatusMessage('Error skipping day. Try again.', 'error');
        }
    } catch (error) {
        console.log('Error skipping day:', error);
        showStatusMessage('Error skipping day. Check server.', 'error');
    }
}

// handle kickflip friday button
async function handleKickflipFridayClick() {
    try {
        const response = await fetch('/kickflip-friday', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // reload the task display
            await loadDailyTask();
            showStatusMessage('Kickflip Friday! Skating task loaded.', 'success');
        } else {
            showStatusMessage('Error loading skating task. Try again.', 'error');
        }
    } catch (error) {
        console.log('Error loading skating task:', error);
        showStatusMessage('Error loading skating task. Check server.', 'error');
    }
}

// show status message
function showStatusMessage(message, type) {
    // create or find status message element
    let statusDiv = document.getElementById('status-message');
    if (!statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.id = 'status-message';
        statusDiv.className = 'status-message';
        document.querySelector('.main-content').appendChild(statusDiv);
    }
    
    statusDiv.textContent = message;
    statusDiv.className = 'status-message ' + type;
    
    // clear after 3 seconds
    setTimeout(function() {
        statusDiv.textContent = '';
        statusDiv.className = 'status-message';
    }, 3000);
}

// when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadUserName();
    loadDailyTask();
    
    // add button listeners
    const submitButton = document.getElementById('submit-task-btn');
    if (submitButton) {
        submitButton.addEventListener('click', handleSubmitClick);
    }
    
    const skipDayButton = document.getElementById('skip-day-btn');
    if (skipDayButton) {
        skipDayButton.addEventListener('click', handleSkipDayClick);
    }
    
    const kickflipFridayButton = document.getElementById('kickflip-friday-btn');
    if (kickflipFridayButton) {
        kickflipFridayButton.addEventListener('click', handleKickflipFridayClick);
    }
});
