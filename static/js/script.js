document.addEventListener('DOMContentLoaded', function() {
    // 處理任務完成狀態切換
    const toggleButtons = document.querySelectorAll('.toggle-complete');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            fetch(`/task/${taskId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const icon = this.querySelector('i');
                    icon.classList.toggle('bi-circle');
                    icon.classList.toggle('bi-check-circle-fill');
                    
                    const taskTitle = this.closest('.list-group-item').querySelector('h5');
                    taskTitle.classList.toggle('text-muted');
                    taskTitle.classList.toggle('text-decoration-line-through');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // 處理任務刪除
    const deleteButtons = document.querySelectorAll('.delete-task');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('確定要刪除這個任務嗎？')) {
                const taskId = this.dataset.taskId;
                fetch(`/task/${taskId}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const taskItem = this.closest('.list-group-item');
                        taskItem.style.opacity = '0';
                        setTimeout(() => {
                            taskItem.remove();
                            // 如果沒有任務了，顯示空狀態
                            const taskList = document.querySelector('.list-group');
                            if (taskList && !taskList.children.length) {
                                location.reload();
                            }
                        }, 300);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });

    // 表單驗證
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // 日期選擇器最小日期設置
    const dueDateInput = document.getElementById('due_date');
    if (dueDateInput) {
        const today = new Date().toISOString().split('T')[0];
        dueDateInput.min = today;
    }
}); 