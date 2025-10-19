# AggieQuest - Hackathon Project
# Task management system with web interface
# Built for Texas A&M students during a 12-hour hackathon

from flask import Flask, request, jsonify, send_file
import random
import json
import os
from datetime import datetime

app = Flask(__name__)

# task banks - we loaded these from files
AL_tier1_bank = []
AL_tier2_bank = []
AL_tier3_bank = []
MH_tier1_bank = []
MH_tier2_bank = []
MH_tier3_bank = []
skateboarding_bank = []

# load tasks from files - took us a while to get this working
# TODO: make this more efficient
def load_tasks():
    global AL_tier1_bank, AL_tier2_bank, AL_tier3_bank
    global MH_tier1_bank, MH_tier2_bank, MH_tier3_bank, skateboarding_bank
    
    # load aggie life tasks
    try:
        with open('tasks/aggieLife_T1.txt', 'r', encoding='utf-8') as f:
            AL_tier1_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load AL T1 tasks")
    
    try:
        with open('tasks/aggieLife_T2.txt', 'r', encoding='utf-8') as f:
            AL_tier2_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load AL T2 tasks")
    
    try:
        with open('tasks/aggieLife_T3.txt', 'r', encoding='utf-8') as f:
            AL_tier3_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load AL T3 tasks")
    
    # load personal growth tasks
    try:
        with open('tasks/personalGrowth_T1.txt', 'r', encoding='utf-8') as f:
            MH_tier1_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load MH T1 tasks")
    
    try:
        with open('tasks/personalGrowth_T2.txt', 'r', encoding='utf-8') as f:
            MH_tier2_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load MH T2 tasks")
    
    try:
        with open('tasks/personalGrowth_T3.txt', 'r', encoding='utf-8') as f:
            MH_tier3_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load MH T3 tasks")
    
    # load skating tasks
    try:
        with open('tasks/skatingTasks.txt', 'r', encoding='utf-8') as f:
            skateboarding_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load skating tasks")

# load tasks when we start
load_tasks()

# make sure uploads directory exists
os.makedirs('uploads', exist_ok=True)

# user data stuff - we store this in a json file
def get_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except:
        # default data if file doesn't exist
        return {
            "total_assigned": 0,
            "completed_tasks": [],
            "current_streak": 0,
            "difficulty_preference": "normal",
            "current_task": None,
            "last_task_date": None,
            "name": "",
            "preferred_hour": "12",
            "preferred_minute": "00",
            "preferred_am_pm": "AM",
            "is_skater": False
        }

def save_user_data(data):
    try:
        with open('user_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

# submissions data
def get_submissions():
    try:
        with open('submissions.json', 'r') as f:
            return json.load(f)
    except:
        return {"submissions": []}

def save_submissions(data):
    try:
        with open('submissions.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

# simple task selection - kept it basic
# TODO: add better task selection logic
def get_daily_task():
    user_data = get_user_data()
    
    # check if we already have a task for today
    today = datetime.now().date().isoformat()
    if user_data.get('last_task_date') == today and user_data.get('current_task'):
        return user_data['current_task']
    
    # pick a random category - hardcoded for now
    category = random.choice(['aggieLife', 'personalGrowth'])
    
# pick a random tier (simplified this)
# TODO: make this smarter
    tier = random.choice(['T1', 'T2', 'T3'])
    
    # get the task list
    if category == 'aggieLife':
        if tier == 'T1':
            task_list = AL_tier1_bank
        elif tier == 'T2':
            task_list = AL_tier2_bank
        else:
            task_list = AL_tier3_bank
    else:
        if tier == 'T1':
            task_list = MH_tier1_bank
        elif tier == 'T2':
            task_list = MH_tier2_bank
        else:
            task_list = MH_tier3_bank
    
    if not task_list:
        return {"task": "No tasks available", "task_id": "", "category": "", "tier": ""}
    
    # pick a random task
    task = random.choice(task_list)
    # create task id - simple version
    task_id = f"{category}_{tier}_{int(datetime.now().timestamp())}"
    
    # save the task
    user_data['current_task'] = {
        'task': task,
        'task_id': task_id,
        'category': category,
        'tier': tier,
        'completed': False
    }
    user_data['last_task_date'] = today
    user_data['total_assigned'] += 1
    save_user_data(user_data)
    
    return user_data['current_task']

# complete a task
def complete_task(task_id):
    user_data = get_user_data()
    
    if user_data.get('current_task') and user_data['current_task']['task_id'] == task_id:
        user_data['current_task']['completed'] = True
        user_data['completed_tasks'].append(user_data['current_task'])
        user_data['current_streak'] += 1
        save_user_data(user_data)
        return True
    return False

# add submission
def add_submission(task_id, description, image_filename):
    submissions = get_submissions()
    user_data = get_user_data()
    current_task = user_data.get('current_task')
    
    if current_task and current_task['task_id'] == task_id:
        submission = {
            "task_id": task_id,
            "task_text": current_task['task'],
            "description": description,
            "image_filename": image_filename,
            "date": datetime.now().isoformat()
        }
        submissions["submissions"].append(submission)
        save_submissions(submissions)
        
        # Mark task as completed and increment streak
        user_data['current_task']['completed'] = True
        user_data['completed_tasks'].append(user_data['current_task'])
        user_data['current_streak'] += 1
        user_data['current_task'] = None  # Clear current task
        save_user_data(user_data)
        
        return True
    return False

# Flask routes - learned this from a tutorial
# TODO: add more routes, fix error handling
@app.route('/')
def index():
    return send_file('html/index.html')

@app.route('/index.html')
def index_html():
    return send_file('html/index.html')

@app.route('/gallery.html')
def gallery():
    return send_file('html/gallery.html')

@app.route('/submit.html')
def submit():
    return send_file('html/submit.html')

@app.route('/settings.html')
def settings():
    return send_file('html/settings.html')

@app.route('/script.js')
def script_js():
    return send_file('html/script.js')

@app.route('/submit.js')
def submit_js():
    return send_file('html/submit.js')

@app.route('/settings.js')
def settings_js():
    return send_file('html/settings.js')

@app.route('/gallery.js')
def gallery_js():
    return send_file('html/gallery.js')

@app.route('/index-style.css')
def index_css():
    return send_file('graphics/index-style.css')

@app.route('/logo.png')
def logo():
    return send_file('graphics/logo.png')

@app.route('/gear.png')
def gear():
    return send_file('graphics/gear.png')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(f'uploads/{filename}')

# API endpoints
@app.route('/task')
def api_task():
    task = get_daily_task()
    return jsonify(task)

@app.route('/complete', methods=['POST'])
def api_complete():
    data = request.get_json()
    task_id = data.get('task_id', '')
    
    if complete_task(task_id):
        return jsonify({'success': True, 'message': 'Task completed!'})
    else:
        return jsonify({'success': False, 'message': 'Error completing task'})

@app.route('/submit', methods=['POST'])
def api_submit():
    # handle form submission - had some issues with this
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image uploaded'})
    
    file = request.files['image']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No image selected'})
    
    # save the file
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file.save(os.path.join('uploads', filename))
    
    # get current task
    user_data = get_user_data()
    current_task = user_data.get('current_task')
    
    if not current_task:
        return jsonify({'success': False, 'message': 'No active task'})
    
    # add submission
    if add_submission(current_task['task_id'], description, filename):
        return jsonify({'success': True, 'message': 'Submission saved and task completed!'})
    else:
        return jsonify({'success': False, 'message': 'Error saving submission'})

@app.route('/gallery')
def api_gallery():
    submissions = get_submissions()
    return jsonify(submissions)

@app.route('/settings')
def api_settings():
    user_data = get_user_data()
    return jsonify({
        'name': user_data.get('name', ''),
        'preferred_hour': user_data.get('preferred_hour', '12'),
        'preferred_minute': user_data.get('preferred_minute', '00'),
        'preferred_am_pm': user_data.get('preferred_am_pm', 'AM'),
        'is_skater': user_data.get('is_skater', False),
        'difficulty': user_data.get('difficulty_preference', 'normal')
    })

@app.route('/settings', methods=['POST'])
def api_update_settings():
    data = request.get_json()
    user_data = get_user_data()
    
    # update settings - just copy the data
    if 'name' in data:
        user_data['name'] = data['name']
    if 'preferred_hour' in data:
        user_data['preferred_hour'] = data['preferred_hour']
    if 'preferred_minute' in data:
        user_data['preferred_minute'] = data['preferred_minute']
    if 'preferred_am_pm' in data:
        user_data['preferred_am_pm'] = data['preferred_am_pm']
    if 'is_skater' in data:
        user_data['is_skater'] = data['is_skater']
    if 'difficulty' in data:
        user_data['difficulty_preference'] = data['difficulty']
    
    if save_user_data(user_data):
        return jsonify({'success': True, 'message': 'Settings saved!'})
    else:
        return jsonify({'success': False, 'message': 'Error saving settings'})

@app.route('/streak')
def api_streak():
    user_data = get_user_data()
    return jsonify({'streak': user_data.get('current_streak', 0)})

@app.route('/skip-day', methods=['POST'])
def api_skip_day():
    # simple skip day - just clear current task
    user_data = get_user_data()
    user_data['current_task'] = None
    user_data['last_task_date'] = None
    if save_user_data(user_data):
        return jsonify({'success': True, 'message': 'Skipped to next day'})
    else:
        return jsonify({'success': False, 'message': 'Error skipping day'})

@app.route('/delete-submission', methods=['POST'])
def api_delete_submission():
    data = request.get_json()
    task_id = data.get('task_id', '')
    
    submissions = get_submissions()
    # find and remove the submission
    for i, submission in enumerate(submissions['submissions']):
        if submission['task_id'] == task_id:
            # delete the image file
            try:
                os.remove(f"uploads/{submission['image_filename']}")
            except:
                pass  # ignore errors
            submissions['submissions'].pop(i)
            break
    
    if save_submissions(submissions):
        return jsonify({'success': True, 'message': 'Submission deleted!'})
    else:
        return jsonify({'success': False, 'message': 'Error deleting submission'})

# main function
if __name__ == '__main__':
    print("========================================")
    print("    AggieQuest Hackathon Project")
    print("========================================")
    print("Starting...")
    print("Loading tasks...")
    print(f"Loaded {len(AL_tier1_bank)} AL T1 tasks")
    print(f"Loaded {len(AL_tier2_bank)} AL T2 tasks") 
    print(f"Loaded {len(AL_tier3_bank)} AL T3 tasks")
    print(f"Loaded {len(MH_tier1_bank)} MH T1 tasks")
    print(f"Loaded {len(MH_tier2_bank)} MH T2 tasks")
    print(f"Loaded {len(MH_tier3_bank)} MH T3 tasks")
    print(f"Loaded {len(skateboarding_bank)} Skating tasks")
    print("========================================")
    app.run(debug=True, host='0.0.0.0', port=5000)