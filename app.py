from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 用於 flash 消息

# 模擬資料庫
tasks = []

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        priority = request.form.get('priority')
        
        task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'completed': False
        }
        tasks.append(task)
        flash('任務已成功新增！', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        flash('找不到該任務！', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        task['title'] = request.form.get('title')
        task['description'] = request.form.get('description')
        task['due_date'] = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        task['priority'] = request.form.get('priority')
        task['completed'] = 'completed' in request.form
        
        flash('任務已成功更新！', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_task.html', task=task)

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        task['completed'] = not task['completed']
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000) 