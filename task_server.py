#!/usr/bin/env python3
"""
Task Server - Serves random tasks with intelligent scoring system
"""

import random
import json
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/task':
            # Serve a random task with scoring logic
            task_data = get_smart_task()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(task_data).encode())
        elif self.path == '/settings/difficulty':
            # Get current difficulty preference
            difficulty = get_difficulty_preference()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'difficulty': difficulty}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/complete':
            # Mark current task as complete
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            result = mark_task_complete(data.get('task_id', ''))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        elif self.path == '/settings/difficulty':
            # Update difficulty preference
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            result = update_difficulty_preference(data.get('difficulty', 'normal'))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()

def load_user_data():
    """Load user data from JSON file, create if doesn't exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, 'user_data.json')
    
    default_data = {
        "total_assigned": 0,
        "completed_tasks": [],
        "current_streak": 0,
        "difficulty_preference": "normal",
        "current_task": None
    }
    
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create file with default data
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
            return default_data
    except Exception as e:
        print(f"Error loading user data: {e}")
        return default_data

def save_user_data(data):
    """Save user data to JSON file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, 'user_data.json')
    
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving user data: {e}")
        return False

def calculate_score(user_data):
    """Calculate user score based on completion rate, streak, and recent performance"""
    total_assigned = user_data.get('total_assigned', 0)
    completed_tasks = user_data.get('completed_tasks', [])
    current_streak = user_data.get('current_streak', 0)
    
    if total_assigned == 0:
        return 50  # Default score for new users
    
    # Completion rate (40% weight)
    completion_rate = len(completed_tasks) / total_assigned if total_assigned > 0 else 0
    
    # Streak score (30% weight) - normalize to 0-1 scale
    streak_score = min(current_streak / 10, 1.0)  # Max streak of 10 = 1.0
    
    # Recent performance (30% weight) - completions in last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    recent_completions = [
        task for task in completed_tasks 
        if datetime.fromisoformat(task['timestamp']) > week_ago
    ]
    recent_score = min(len(recent_completions) / 7, 1.0)  # Max 1 completion per day
    
    # Combined score (0-100)
    score = (completion_rate * 40) + (streak_score * 30) + (recent_score * 30)
    return min(score, 100)

def get_tier_probabilities(score, difficulty_preference):
    """Get task tier probabilities based on score and difficulty preference"""
    # Base probabilities by score range
    if score <= 33:
        base_probs = {'T1': 0.70, 'T2': 0.25, 'T3': 0.05}
    elif score <= 66:
        base_probs = {'T1': 0.15, 'T2': 0.70, 'T3': 0.15}
    else:
        base_probs = {'T1': 0.05, 'T2': 0.25, 'T3': 0.70}
    
    # Adjust based on difficulty preference
    if difficulty_preference == 'easier':
        # Shift probabilities down one tier
        adjusted_probs = {
            'T1': base_probs['T1'] + base_probs['T2'] * 0.3,
            'T2': base_probs['T2'] * 0.7 + base_probs['T3'] * 0.3,
            'T3': base_probs['T3'] * 0.7
        }
    elif difficulty_preference == 'harder':
        # Shift probabilities up one tier
        adjusted_probs = {
            'T1': base_probs['T1'] * 0.7,
            'T2': base_probs['T1'] * 0.3 + base_probs['T2'] * 0.7,
            'T3': base_probs['T2'] * 0.3 + base_probs['T3']
        }
    else:  # normal
        adjusted_probs = base_probs
    
    return adjusted_probs

def select_task_tier(score, difficulty_preference):
    """Select task tier based on weighted probabilities"""
    probs = get_tier_probabilities(score, difficulty_preference)
    rand = random.random()
    
    cumulative = 0
    for tier, prob in probs.items():
        cumulative += prob
        if rand <= cumulative:
            return tier
    
    return 'T2'  # Fallback

def load_tasks_from_file(category, tier):
    """Load tasks from specific category and tier file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    task_file = os.path.join(script_dir, 'tasks', f'{category}_{tier}.txt')
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Skip the first line (count) and get all tasks
        tasks = [line.strip() for line in lines[1:] if line.strip()]
        return tasks
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading tasks from {task_file}: {e}")
        return []

def get_smart_task():
    """Get a smart task based on user performance and preferences"""
    user_data = load_user_data()
    score = calculate_score(user_data)
    difficulty_preference = user_data.get('difficulty_preference', 'normal')
    
    # Select category (50/50 split)
    category = random.choice(['aggieLife', 'personalGrowth'])
    
    # Select tier based on score and preference
    tier = select_task_tier(score, difficulty_preference)
    
    # Load tasks from selected file
    tasks = load_tasks_from_file(category, tier)
    
    if not tasks:
        return {
            'task': 'No tasks available',
            'task_id': '',
            'category': category,
            'tier': tier,
            'score': score
        }
    
    # Select random task
    selected_task = random.choice(tasks)
    task_id = f"{category}_{tier}_{len(user_data.get('completed_tasks', []))}"
    
    # Update user data with new task
    user_data['current_task'] = {
        'task_id': task_id,
        'task': selected_task,
        'category': category,
        'tier': tier,
        'assigned_at': datetime.now().isoformat()
    }
    user_data['total_assigned'] += 1
    save_user_data(user_data)
    
    return {
        'task': selected_task,
        'task_id': task_id,
        'category': category,
        'tier': tier,
        'score': score  # For debugging - remove in production
    }

def mark_task_complete(task_id):
    """Mark the current task as complete and update scoring"""
    user_data = load_user_data()
    current_task = user_data.get('current_task')
    
    if not current_task or current_task.get('task_id') != task_id:
        return {'success': False, 'message': 'Task not found or already completed'}
    
    # Add to completed tasks
    completed_task = {
        'task_id': task_id,
        'task': current_task.get('task', ''),
        'category': current_task.get('category', ''),
        'tier': current_task.get('tier', ''),
        'completed_at': datetime.now().isoformat(),
        'timestamp': datetime.now().isoformat()
    }
    
    user_data['completed_tasks'].append(completed_task)
    
    # Update streak
    user_data['current_streak'] += 1
    
    # Clear current task
    user_data['current_task'] = None
    
    # Save updated data
    if save_user_data(user_data):
        return {'success': True, 'message': 'Task marked as complete', 'new_score': calculate_score(user_data)}
    else:
        return {'success': False, 'message': 'Error saving completion'}

def get_difficulty_preference():
    """Get current difficulty preference"""
    user_data = load_user_data()
    return user_data.get('difficulty_preference', 'normal')

def update_difficulty_preference(difficulty):
    """Update difficulty preference"""
    if difficulty not in ['easier', 'normal', 'harder']:
        return {'success': False, 'message': 'Invalid difficulty preference'}
    
    user_data = load_user_data()
    user_data['difficulty_preference'] = difficulty
    
    if save_user_data(user_data):
        return {'success': True, 'message': f'Difficulty preference set to {difficulty}'}
    else:
        return {'success': False, 'message': 'Error saving preference'}

def run_server(port=8000):
    """Start the task server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TaskHandler)
    print(f"Task server running on http://localhost:{port}")
    print("Visit http://localhost:8000/task to get a random task")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
