# src/planner.py
from typing import List, Dict, Any

def generate_execution_steps(task: Dict[str, Any]) -> List[str]:
    """
    Generate 3-5 execution steps for a task.
    """
    title = task.get('title', '').lower()
    
    # Simple rule-based step generation
    if 'document' in title or 'draft' in title:
        return [
            "Outline the main sections",
            "Draft initial content", 
            "Review and revise",
            "Share for feedback"
        ]
    elif 'research' in title or 'analyze' in title:
        return [
            "Gather relevant data/sources",
            "Analyze patterns/trends",
            "Summarize key findings",
            "Prepare recommendations"
        ]
    elif 'meeting' in title or 'demo' in title:
        return [
            "Prepare agenda/materials",
            "Schedule with participants", 
            "Conduct the session",
            "Document outcomes"
        ]
    elif 'update' in title or 'implement' in title:
        return [
            "Assess current state",
            "Plan changes",
            "Implement updates",
            "Test and verify"
        ]
    else:
        return [
            "Define detailed requirements",
            "Execute the core work",
            "Review quality",
            "Deliver outcomes"
        ]

def plan_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add execution plans to all tasks.
    """
    planned_tasks = []
    
    for task in tasks:
        planned_task = task.copy()
        planned_task['execution_steps'] = generate_execution_steps(task)
        planned_task['estimated_effort'] = estimate_effort(task)
        planned_tasks.append(planned_task)
    
    return planned_tasks

def estimate_effort(task: Dict[str, Any]) -> str:
    """
    Estimate effort as Small/Medium/Large.
    """
    title = task.get('title', '')
    description = task.get('description', '')
    full_text = (title + ' ' + description).lower()
    
    if any(word in full_text for word in ['quick', 'small', 'minor', 'update', 'check']):
        return "Small"
    elif any(word in full_text for word in ['research', 'draft', 'prepare', 'coordinate']):
        return "Medium" 
    else:
        return "Large"