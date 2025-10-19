// main page script - still figuring this out
// TODO: make this work better, fix bugs

let countdownInterval = null;

// load user name - took us a while to get this working
async function loadUserName() {
    const userNameElement = document.querySelector('.user-name');
    if (!userNameElement) return;
    
    try {
        const response = await fetch('http://127.0.0.1:5000/settings');
        const data = await response.json();
        
        if (data.name) {
            userNameElement.textContent = data.name;
        } else {
            userNameElement.textContent = 'User';
        }
    } catch (error) {
        console.log('Error loading name:', error);
        userNameElement.textContent = 'User';
    }
}

// load daily task
async function loadDailyTask() {
    const taskDisplay = document.getElementById('task-display');
    if (!taskDisplay) return;
    
    try {
        const response = await fetch('http://127.0.0.1:5000/task');
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

// load streak - simple version
async function loadStreak() {
    const streakDisplay = document.getElementById('streak-display');
    if (!streakDisplay) return;
    
    try {
        const response = await fetch('http://127.0.0.1:5000/streak');
        const data = await response.json();
        
        const dayText = data.streak === 1 ? 'day' : 'days';
        streakDisplay.textContent = data.streak + ' ' + dayText;
        streakDisplay.setAttribute('data-streak', data.streak);
    } catch (error) {
        console.log('Error loading streak:', error);
        streakDisplay.textContent = '0 days';
        streakDisplay.setAttribute('data-streak', '0');
    }
}

// simple countdown - basic version
function startCountdown() {
    const countdownTimer = document.getElementById('countdown-timer');
    if (!countdownTimer) return;
    
    // Get countdown from localStorage or start with 2 hours
    let seconds = parseInt(localStorage.getItem('countdownSeconds')) || 7200; // 2 hours for testing
    
    function updateCountdown() {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        countdownTimer.textContent = 
            hours.toString().padStart(2, '0') + ':' +
            mins.toString().padStart(2, '0') + ':' +
            secs.toString().padStart(2, '0');
        
        if (seconds <= 0) {
            countdownTimer.textContent = '00:00:00';
            localStorage.removeItem('countdownSeconds'); // Clear when done
            location.reload(); // refresh page
            return;
        }
        
        seconds--;
        localStorage.setItem('countdownSeconds', seconds); // Save current countdown
    }
    
    updateCountdown();
    countdownInterval = setInterval(updateCountdown, 1000);
}

// handle submit button
function handleSubmitClick() {
    window.location.href = 'submit.html';
}

// skip day button - had some issues with this
async function handleSkipDay() {
    const skipButton = document.getElementById('skip-day-btn');
    if (!skipButton) return;
    
    skipButton.disabled = true;
    skipButton.textContent = 'Skipping...';
    
    try {
        const response = await fetch('http://127.0.0.1:5000/skip-day', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.log('Error skipping day:', error);
        alert('Error skipping day. Check server.');
    } finally {
        skipButton.disabled = false;
        skipButton.textContent = '⚠️ Skip to Next Day (Testing)';
    }
}

// when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadUserName();
    loadDailyTask();
    loadStreak();
    startCountdown();
    
    // add button listeners
    const submitButton = document.getElementById('submit-task-btn');
    if (submitButton) {
        submitButton.addEventListener('click', handleSubmitClick);
    }
    
    const skipButton = document.getElementById('skip-day-btn');
    if (skipButton) {
        skipButton.addEventListener('click', handleSkipDay);
    }
});

// cleanup
window.addEventListener('beforeunload', function() {
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
});