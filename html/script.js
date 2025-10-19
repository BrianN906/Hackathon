// main page script - still figuring this out
// TODO: make this work better, fix bugs


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




// handle submit button
function handleSubmitClick() {
    window.location.href = 'submit.html';
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
    
});
