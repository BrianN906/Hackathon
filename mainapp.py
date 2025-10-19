from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import random
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# task banks - we loaded these from files
al_tier1_bank = []
al_tier2_bank = []
al_tier3_bank = []
mh_tier1_bank = []
mh_tier2_bank = []
mh_tier3_bank = []
skating_tasks_bank = []

# load tasks from files - took us a while to get this working
def load_tasks():
    global al_tier1_bank, al_tier2_bank, al_tier3_bank
    global mh_tier1_bank, mh_tier2_bank, mh_tier3_bank
    global skating_tasks_bank
    
    # load aggie life tasks
    try:
        with open('tasks/aggieLife_T1.txt', 'r', encoding='utf-8') as f:
            al_tier1_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load al t1 tasks")
    
    try:
        with open('tasks/aggieLife_T2.txt', 'r', encoding='utf-8') as f:
            al_tier2_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load al t2 tasks")
    
    try:
        with open('tasks/aggieLife_T3.txt', 'r', encoding='utf-8') as f:
            al_tier3_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load al t3 tasks")
    
    # load personal growth tasks
    try:
        with open('tasks/personalGrowth_T1.txt', 'r', encoding='utf-8') as f:
            mh_tier1_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load mh t1 tasks")
    
    try:
        with open('tasks/personalGrowth_T2.txt', 'r', encoding='utf-8') as f:
            mh_tier2_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load mh t2 tasks")
    
    try:
        with open('tasks/personalGrowth_T3.txt', 'r', encoding='utf-8') as f:
            mh_tier3_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
    except:
        print("couldn't load mh t3 tasks")
    
    # load skating tasks
    try:
        with open('tasks/skatingTasks.txt', 'r', encoding='utf-8') as f:
            skating_tasks_bank = [line.strip() for line in f.readlines()[1:] if line.strip()]
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
            data = json.load(f)
            return data
    except:
        # default data if file doesn't exist
        return {
            "completed_tasks": [],
            "difficulty_preference": "normal",
            "current_task": None,
            "last_task_date": None,
            "name": "",
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
def get_daily_task():
    user_data = get_user_data()
    
    # check if we already have a task for today
    today = datetime.now().date().isoformat()
    if user_data.get('last_task_date') == today and user_data.get('current_task'):
        return user_data['current_task']
    
    # randomly select from all 6 task files equally
    all_task_banks = [
        (al_tier1_bank, 'aggieLife', 'T1'),
        (al_tier2_bank, 'aggieLife', 'T2'),
        (al_tier3_bank, 'aggieLife', 'T3'),
        (mh_tier1_bank, 'personalGrowth', 'T1'),
        (mh_tier2_bank, 'personalGrowth', 'T2'),
        (mh_tier3_bank, 'personalGrowth', 'T3')
    ]
    
    # filter out empty banks
    available_banks = [(bank, cat, tier) for bank, cat, tier in all_task_banks if bank]
    
    if not available_banks:
        return {"task": "No tasks available", "task_id": "", "category": "", "tier": ""}
    
    # pick a random bank
    task_list, category, tier = random.choice(available_banks)
    
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
    save_user_data(user_data)
    
    return user_data['current_task']

# kickflip friday task selection
def get_kickflip_friday_task():
    user_data = get_user_data()
    
    if not skating_tasks_bank:
        return {"task": "No skating tasks available", "task_id": "", "category": "skating", "tier": "special"}
    
    # pick a random skating task
    task = random.choice(skating_tasks_bank)
    # create task id - simple version
    task_id = f"skating_special_{int(datetime.now().timestamp())}"
    
    # save the task
    user_data['current_task'] = {
        'task': task,
        'task_id': task_id,
        'category': 'skating',
        'tier': 'special',
        'completed': False
    }
    user_data['last_task_date'] = datetime.now().date().isoformat()
    save_user_data(user_data)
    
    return user_data['current_task']

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
        
        # create a copy of the task before clearing it
        completed_task = user_data['current_task'].copy()
        completed_task['completed'] = True
        user_data['completed_tasks'].append(completed_task)
        
        user_data['current_task'] = None  # clear current task
        save_user_data(user_data)
        
        return True
    return False

# flask routes - learned this from a tutorial
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

# api endpoints
@app.route('/task')
def api_task():
    task = get_daily_task()
    return jsonify(task)

@app.route('/skip-day', methods=['POST'])
def api_skip_day():
    user_data = get_user_data()
    # clear current task and date to force new task generation
    user_data['current_task'] = None
    user_data['last_task_date'] = None
    save_user_data(user_data)
    
    # generate new task
    task = get_daily_task()
    return jsonify({'success': True, 'task': task})

@app.route('/kickflip-friday', methods=['POST'])
def api_kickflip_friday():
    task = get_kickflip_friday_task()
    return jsonify({'success': True, 'task': task})


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
        'preferred_hour': '12',  # not implemented yet
        'preferred_minute': '00',  # not implemented yet
        'preferred_am_pm': 'AM',  # not implemented yet
        'is_skater': user_data.get('is_skater', False),
        'difficulty': user_data.get('difficulty_preference', 'normal')  # not implemented yet
    })

@app.route('/settings', methods=['POST'])
def api_update_settings():
    try:
        data = request.get_json()
        
        # get current user data
        user_data = get_user_data()
        
        # update settings - allow empty name to reset to default
        user_data['name'] = data.get('name', '').strip() if data.get('name') else ''
        user_data['difficulty_preference'] = data.get('difficulty', 'normal')
        user_data['is_skater'] = data.get('is_skater', False)
        
        # save updated data
        if save_user_data(user_data):
            return jsonify({'success': True, 'message': 'Settings saved successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Error saving settings'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing settings: {str(e)}'})



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
    total_tasks = len(al_tier1_bank) + len(al_tier2_bank) + len(al_tier3_bank) + len(mh_tier1_bank) + len(mh_tier2_bank) + len(mh_tier3_bank) + len(skating_tasks_bank)
    print(f"loaded {total_tasks} tasks - server ready!")
    app.run(debug=False, host='0.0.0.0', port=5000)