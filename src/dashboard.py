# src/dashboard.py
from typing import List, Dict, Any
from datetime import datetime

def generate_task_dashboard(tasks: List[Dict[str, Any]]) -> str:
    """
    Generate a simple HTML dashboard for tasks.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meeting Action Items Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .task { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .high-priority { border-left: 5px solid #e74c3c; }
            .medium-priority { border-left: 5px solid #f39c12; }
            .low-priority { border-left: 5px solid #27ae60; }
            .task-header { display: flex; justify-content: space-between; }
            .steps { margin-left: 20px; color: #666; }
            .stats { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Meeting Action Items Dashboard</h1>
        <p>Generated on {timestamp}</p>
        
        <div class="stats">
            <h3>Summary</h3>
            <p>Total Tasks: {total_tasks} | High Priority: {high_priority} | Medium Priority: {medium_priority} | Low Priority: {low_priority}</p>
        </div>
        
        <div id="tasks">
            {tasks_html}
        </div>
    </body>
    </html>
    """
    
    # Calculate stats
    total_tasks = len(tasks)
    high_priority = sum(1 for task in tasks if task.get('priority', '').lower() == 'high')
    medium_priority = sum(1 for task in tasks if task.get('priority', '').lower() == 'medium')
    low_priority = sum(1 for task in tasks if task.get('priority', '').lower() == 'low')
    
    tasks_html = ""
    for task in tasks:
        priority_class = task.get('priority', 'medium').lower()
        steps_html = "".join([f"<li>{step}</li>" for step in task.get('execution_steps', [])])
        
        task_html = f"""
        <div class="task {priority_class}-priority">
            <div class="task-header">
                <h3>{task.get('title', 'No title')}</h3>
                <span><strong>{task.get('priority', 'Medium')}</strong> Priority</span>
            </div>
            <p><strong>Owner:</strong> {task.get('owner', 'TBD')} { '✅' if task.get('owner_valid') else '' }</p>
            <p><strong>Deadline:</strong> {task.get('deadline', 'TBD')}</p>
            <p><strong>Effort:</strong> {task.get('estimated_effort', 'Medium')}</p>
            <p><strong>Description:</strong> {task.get('description', '')}</p>
            <p><strong>Execution Steps:</strong></p>
            <ol class="steps">{steps_html}</ol>
            <p><em>Evidence: "{task.get('evidence', '')}"</em></p>
        </div>
        """
        tasks_html += task_html
    
    return html_template.replace("{timestamp}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))\
                       .replace("{total_tasks}", str(total_tasks))\
                       .replace("{high_priority}", str(high_priority))\
                       .replace("{medium_priority}", str(medium_priority))\
                       .replace("{low_priority}", str(low_priority))\
                       .replace("{tasks_html}", tasks_html)

def display_task_summary(tasks: List[Dict[str, Any]]) -> None:
    """
    Print a summary of tasks to console.
    """
    print("\n📊 TASK SUMMARY:")
    print("=" * 50)
    print(f"Total Tasks: {len(tasks)}")
    
    priorities = {}
    efforts = {}
    owners = {}
    
    for task in tasks:
        priority = task.get('priority', 'Unknown')
        effort = task.get('estimated_effort', 'Unknown')
        owner = task.get('owner', 'Unassigned')
        
        priorities[priority] = priorities.get(priority, 0) + 1
        efforts[effort] = efforts.get(effort, 0) + 1
        owners[owner] = owners.get(owner, 0) + 1
    
    print(f"\n📈 By Priority:")
    for priority, count in priorities.items():
        print(f"   {priority}: {count}")
    
    print(f"\n⚡ By Effort:")
    for effort, count in efforts.items():
        print(f"   {effort}: {count}")
    
    print(f"\n👥 By Owner:")
    for owner, count in owners.items():
        print(f"   {owner}: {count}")