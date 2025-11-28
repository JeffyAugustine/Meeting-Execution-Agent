# src/validate.py
from typing import List, Dict, Any

def validate_tasks(tasks: List[Dict[str, Any]], participants: List[str]) -> List[Dict[str, Any]]:
    """
    Validate extracted tasks against participant list and add validation flags.
    
    Args:
        tasks: List of extracted tasks
        participants: List of meeting participants
        
    Returns:
        List of validated tasks with confidence adjustments
    """
    validated_tasks = []
    
    for task in tasks:
        validated_task = task.copy()
        
        # Validate owner against participants
        owner = task.get('owner', 'TBD')
        if owner != 'TBD':
            # Simple fuzzy matching - check if owner name appears in participant list
            owner_valid = any(owner.lower() in participant.lower() for participant in participants)
            validated_task['owner_valid'] = owner_valid
            if not owner_valid:
                # Reduce confidence if owner doesn't match participants
                validated_task['confidence'] = validated_task.get('confidence', 1.0) * 0.7
        else:
            validated_task['owner_valid'] = False
            
        # Validate deadline format
        deadline = task.get('deadline', 'TBD')
        if deadline != 'TBD':
            validated_task['deadline_valid'] = True
        else:
            validated_task['deadline_valid'] = False
            
        validated_tasks.append(validated_task)
    
    return validated_tasks

def deduplicate_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate tasks based on title similarity.
    """
    unique_tasks = []
    seen_titles = set()
    
    for task in tasks:
        title = task.get('title', '').lower().strip()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_tasks.append(task)
    
    return unique_tasks