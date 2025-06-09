import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models import db, Task

app = Flask(__name__)
app.secret_key = 'your-secret-key'

DB_NAME = 'tasks.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)

if not os.path.exists('instance\\' + DB_NAME):
    with app.app_context():
        db.create_all()
        db.session.commit()

@app.route('/')
def index():
    selected_category = request.args.get('category')

    if selected_category == "":
        tasks = Task.query.all()
    elif selected_category:
        tasks = Task.query.filter(Task.category == selected_category).all()
    else:
        tasks = Task.query.all()

    categories = db.session.query(Task.category)\
        .filter(Task.category.isnot(None))\
        .filter(Task.category != "")\
        .distinct().all()
    categories = [c[0] for c in categories]


    return render_template(
        'index.html',
        tasks=tasks,
        categories=categories,
        selected_category=selected_category
    )


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        priority = request.form.get('priority')

        task = Task(
            category=category,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            completed=False
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        task.category = request.form.get('category')
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        task.priority = request.form.get('priority')
        task.category = request.form.get('category')
        task.completed = 'completed' in request.form

        db.session.commit()
        flash('任務已成功更新！', 'success')
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)