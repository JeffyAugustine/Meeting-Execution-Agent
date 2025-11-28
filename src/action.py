# src/action.py
import json
import csv
from typing import List, Dict, Any
from datetime import datetime

def generate_followup_email(meeting_summary: str, tasks: List[Dict[str, Any]], participants: List[str]) -> str:
    """
    Generate a follow-up email draft summarizing the meeting outcomes.
    """
    email_subject = f"Action Items from Meeting - {datetime.now().strftime('%Y-%m-%d')}"
    
    email_body = f"""Hi team,

Here are the action items from our recent meeting:

MEETING SUMMARY:
{meeting_summary}

ACTION ITEMS:
"""
    
    for i, task in enumerate(tasks, 1):
        email_body += f"""
{i}. {task.get('title', 'No title')}
   • Owner: {task.get('owner', 'TBD')}
   • Deadline: {task.get('deadline', 'TBD')}
   • Priority: {task.get('priority', 'Medium')}
   • Effort: {task.get('estimated_effort', 'Medium')}
"""
    
    email_body += f"""

Please confirm your assigned tasks and deadlines by replying to this email.

Best regards,
Meeting Assistant
"""

    return email_subject, email_body

def export_to_csv(tasks: List[Dict[str, Any]], filename: str) -> None:
    """
    Export tasks to CSV format.
    """
    if not tasks:
        return
        
    fieldnames = ['title', 'description', 'owner', 'deadline', 'priority', 'confidence', 
                  'estimated_effort', 'owner_valid', 'evidence']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for task in tasks:
            # Only include relevant fields
            row = {field: task.get(field, '') for field in fieldnames}
            writer.writerow(row)

def export_to_json(tasks: List[Dict[str, Any]], filename: str) -> None:
    """
    Export tasks to JSON format.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2)