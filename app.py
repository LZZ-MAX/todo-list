import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'
DB_NAME = 'instance/tasks.db'

# 初始化資料庫
def init_db():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 取得資料庫連線
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 將資料庫行轉換為任務字典
def row_to_task(row):
    task = dict(row)
    if task['due_date']:
        task['due_date'] = datetime.strptime(task['due_date'], '%Y-%m-%d')
    else:
        task['due_date'] = None
    return task

# 取得所有任務
def get_tasks(category=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute('SELECT * FROM tasks WHERE category = ?', (category,))
    else:
        cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()
    conn.close()
    return [row_to_task(row) for row in rows]

# 取得分類清單
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM tasks WHERE category IS NOT NULL AND category != ""')
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories

# 路由設定
@app.route('/')
def index():
    selected_category = request.args.get('category')
    tasks = get_tasks(selected_category)
    categories = get_categories()
    return render_template('index.html', tasks=tasks, categories=categories, selected_category=selected_category)

# 添加任務
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date') or None
        priority = request.form.get('priority')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (category, title, description, due_date, priority, completed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, title, description, due_date, priority, 0))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_task.html')

# 編輯任務
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date') or None
        priority = request.form.get('priority')
        completed = 1 if request.form.get('completed') else 0

        cursor.execute('''
            UPDATE tasks
            SET category = ?, title = ?, description = ?, due_date = ?, priority = ?, completed = ?
            WHERE id = ?
        ''', (category, title, description, due_date, priority, completed, task_id))
        conn.commit()
        conn.close()
        flash('任務已成功更新！', 'success')
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = row_to_task(cursor.fetchone())
    conn.close()
    return render_template('edit_task.html', task=task)

# 切換任務完成狀態
@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    if row:
        new_completed = 0 if row['completed'] else 1
        cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_completed, task_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    conn.close()
    return jsonify({'success': False}), 404

# 刪除任務
@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
