// gallery page - still working on this

// when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadSubmissions();
    
    // back button
    const backToHomeBtn = document.getElementById('back-to-home-btn');
    if (backToHomeBtn) {
        backToHomeBtn.addEventListener('click', function() {
            window.location.href = 'index.html';
        });
    }
});

// load submissions - basic version
async function loadSubmissions() {
    try {
        const response = await fetch('/gallery');
        const data = await response.json();
        
        if (data.submissions && data.submissions.length > 0) {
            displaySubmissions(data.submissions);
        } else {
            displayEmptyState();
        }
    } catch (error) {
        console.log('Error loading submissions:', error);
        displayErrorState();
    }
}

// show submissions - kept it simple
function displaySubmissions(submissions) {
    const galleryContainer = document.querySelector('.gallery-container');
    galleryContainer.innerHTML = '';
    
    // just show them in order
    submissions.forEach(function(submission) {
        const card = createSubmissionCard(submission);
        galleryContainer.appendChild(card);
    });
}

// create card
function createSubmissionCard(submission) {
    const card = document.createElement('div');
    card.className = 'gallery-card';
    card.dataset.taskId = submission.task_id;
    
    // format date
    const date = new Date(submission.date);
    const formattedDate = date.toLocaleDateString();
    
    card.innerHTML = 
        '<div class="card-image-container">' +
            '<img src="/uploads/' + submission.image_filename + '" ' +
                 'alt="Submission image" class="card-image">' +
        '</div>' +
        '<div class="card-content">' +
            '<div class="card-header">' +
                '<h3 class="card-task">' + submission.task_text + '</h3>' +
            '</div>' +
            '<div class="card-description">' +
                '<p>' + (submission.description || 'No description') + '</p>' +
            '</div>' +
            '<div class="card-footer">' +
                '<span class="card-date">' + formattedDate + '</span>' +
                '<button class="delete-btn" onclick="deleteSubmission(\'' + submission.task_id + '\')">' +
                    'Delete' +
                '</button>' +
            '</div>' +
        '</div>';
    
    return card;
}

// empty state
function displayEmptyState() {
    const galleryContainer = document.querySelector('.gallery-container');
    galleryContainer.innerHTML = 
        '<div class="empty-state">' +
            '<h3>No submissions yet!</h3>' +
            '<p>Complete some tasks to see them here.</p>' +
            '<button onclick="window.location.href=\'submit.html\'">Submit Task</button>' +
        '</div>';
}

// error state
function displayErrorState() {
    const galleryContainer = document.querySelector('.gallery-container');
    galleryContainer.innerHTML = 
        '<div class="error-state">' +
            '<h3>Error loading submissions</h3>' +
            '<p>Try again later.</p>' +
            '<button onclick="loadSubmissions()">Try Again</button>' +
        '</div>';
}

// delete submission - tricky to get working
async function deleteSubmission(taskId) {
    if (!confirm('Delete this submission?')) {
        return;
    }
    
    try {
        const response = await fetch('/delete-submission', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task_id: taskId })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // remove from page
            const card = document.querySelector('[data-task-id="' + taskId + '"]');
            if (card) {
                card.remove();
            }
            
            // check if empty
            const remainingCards = document.querySelectorAll('.gallery-card');
            if (remainingCards.length === 0) {
                displayEmptyState();
            }
            
            alert('Deleted!');
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.log('Error deleting:', error);
        alert('Error deleting. Try again.');
    }
}