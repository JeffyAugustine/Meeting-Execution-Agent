# src/evaluate.py
import pandas as pd
import json
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re

def load_ground_truth(csv_path: str) -> pd.DataFrame:
    """
    Load ground truth annotations from CSV.
    Expected columns: transcript_id, task_id, task_title, task_description, owner, 
                     owner_email, deadline, priority, evidence_start, evidence_text
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded ground truth: {len(df)} tasks from {len(df['transcript_id'].unique())} meetings")
        print(f"📊 Ground truth columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ Error loading ground truth: {e}")
        return pd.DataFrame()

def load_ai_predictions(json_path: str) -> List[Dict[str, Any]]:
    """
    Load AI-generated predictions from JSON output.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Extract tasks from different possible structures
        if 'tasks' in data:
            tasks = data['tasks']
        elif 'planned_tasks' in data:
            tasks = data['planned_tasks']
        elif 'analysis_results' in data and 'tasks' in data['analysis_results']:
            tasks = data['analysis_results']['tasks']
        else:
            tasks = data  # Assume it's directly the tasks list
            
        print(f"✅ Loaded AI predictions: {len(tasks)} tasks")
        return tasks
    except Exception as e:
        print(f"❌ Error loading AI predictions: {e}")
        return []

def preprocess_text(text: str) -> str:
    """
    Normalize text for comparison.
    """
    if not isinstance(text, str):
        return ""
    # Convert to lowercase, remove extra spaces, and basic normalization
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text

def calculate_task_matching(ground_truth_tasks: List[str], ai_tasks: List[str]) -> Tuple[float, float, float]:
    """
    Calculate precision, recall, and F1 for task extraction.
    Uses text similarity matching.
    """
    if not ground_truth_tasks or not ai_tasks:
        return 0.0, 0.0, 0.0
    
    # Normalize tasks
    gt_normalized = [preprocess_text(task) for task in ground_truth_tasks]
    ai_normalized = [preprocess_text(task) for task in ai_tasks]
    
    # Calculate matches using containment (more flexible than exact match)
    true_positives = 0
    matched_gt_indices = set()
    
    for i, ai_task in enumerate(ai_normalized):
        for j, gt_task in enumerate(gt_normalized):
            if j in matched_gt_indices:
                continue
            # Check if tasks are similar (either contains the other or significant overlap)
            words_ai = set(ai_task.split())
            words_gt = set(gt_task.split())
            
            # Calculate Jaccard similarity
            intersection = len(words_ai.intersection(words_gt))
            union = len(words_ai.union(words_gt))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0.3:  # Threshold for matching
                true_positives += 1
                matched_gt_indices.add(j)
                break
    
    precision = true_positives / len(ai_normalized) if ai_normalized else 0
    recall = true_positives / len(gt_normalized) if gt_normalized else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

def calculate_owner_accuracy(ground_truth_owners: List[str], ai_owners: List[str]) -> float:
    """
    Calculate owner assignment accuracy.
    """
    if not ground_truth_owners or not ai_owners:
        return 0.0
    
    correct = 0
    total = min(len(ground_truth_owners), len(ai_owners))
    
    for i in range(total):
        gt_owner = preprocess_text(ground_truth_owners[i]) if i < len(ground_truth_owners) else ""
        ai_owner = preprocess_text(ai_owners[i]) if i < len(ai_owners) else ""
        
        # Simple matching - can be enhanced with fuzzy matching
        if gt_owner and ai_owner and (gt_owner in ai_owner or ai_owner in gt_owner):
            correct += 1
    
    return correct / total if total > 0 else 0

def calculate_priority_accuracy(ground_truth_priorities: List[str], ai_priorities: List[str]) -> float:
    """
    Calculate priority assignment accuracy.
    """
    if not ground_truth_priorities or not ai_priorities:
        return 0.0
    
    correct = 0
    total = min(len(ground_truth_priorities), len(ai_priorities))
    
    for i in range(total):
        gt_priority = preprocess_text(ground_truth_priorities[i]) if i < len(ground_truth_priorities) else ""
        ai_priority = preprocess_text(ai_priorities[i]) if i < len(ai_priorities) else ""
        
        if gt_priority and ai_priority and gt_priority == ai_priority:
            correct += 1
    
    return correct / total if total > 0 else 0

def evaluate_meeting(transcript_id: str, ground_truth_df: pd.DataFrame, ai_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate AI performance for a specific meeting against ground truth.
    """
    # Filter ground truth for this meeting
    gt_meeting_tasks = ground_truth_df[ground_truth_df['transcript_id'] == transcript_id]
    
    if gt_meeting_tasks.empty:
        return {"error": f"No ground truth found for {transcript_id}"}
    
    # Extract ground truth data
    gt_titles = gt_meeting_tasks['task_title'].tolist()
    gt_owners = gt_meeting_tasks['owner'].tolist()
    gt_priorities = gt_meeting_tasks['priority'].tolist()
    
    # Extract AI predictions
    ai_titles = [task.get('title', '') for task in ai_tasks]
    ai_owners = [task.get('owner', '') for task in ai_tasks]
    ai_priorities = [task.get('priority', '') for task in ai_tasks]
    
    # Calculate metrics
    task_precision, task_recall, task_f1 = calculate_task_matching(gt_titles, ai_titles)
    owner_accuracy = calculate_owner_accuracy(gt_owners, ai_owners)
    priority_accuracy = calculate_priority_accuracy(gt_priorities, ai_priorities)
    
    return {
        'transcript_id': transcript_id,
        'ground_truth_tasks': len(gt_meeting_tasks),
        'ai_predicted_tasks': len(ai_tasks),
        'task_precision': round(task_precision, 3),
        'task_recall': round(task_recall, 3),
        'task_f1': round(task_f1, 3),
        'owner_accuracy': round(owner_accuracy, 3),
        'priority_accuracy': round(priority_accuracy, 3),
        'details': {
            'ground_truth_titles': gt_titles,
            'ai_titles': ai_titles,
            'ground_truth_owners': gt_owners,
            'ai_owners': ai_owners
        }
    }

def run_comprehensive_evaluation(ground_truth_path: str, ai_outputs_dir: str = '../assets') -> Dict[str, Any]:
    """
    Run comprehensive evaluation across all meetings.
    """
    print("🔍 RUNNING COMPREHENSIVE EVALUATION")
    print("=" * 60)
    
    # Load ground truth
    ground_truth_df = load_ground_truth(ground_truth_path)
    if ground_truth_df.empty:
        return {"error": "Could not load ground truth"}
    
    # Get all meeting IDs from ground truth
    meeting_ids = ground_truth_df['transcript_id'].unique()
    print(f"📊 Evaluating {len(meeting_ids)} meetings: {list(meeting_ids)}")
    
    results = {}
    all_metrics = []
    
    for meeting_id in meeting_ids:
        print(f"\n📋 Evaluating {meeting_id}...")
        
        # Look for the correct AI output file
        ai_output_path = f"{ai_outputs_dir}/{meeting_id}_output.json"
        if not os.path.exists(ai_output_path):
            # Try alternative path
            ai_output_path = f"{ai_outputs_dir}/batch_results/{meeting_id}_output.json"
            if not os.path.exists(ai_output_path):
                print(f"   ❌ AI output not found: {ai_output_path}")
                continue
        
        ai_tasks = load_ai_predictions(ai_output_path)
        
        # Evaluate this meeting
        meeting_results = evaluate_meeting(meeting_id, ground_truth_df, ai_tasks)
        
        if 'error' not in meeting_results:
            results[meeting_id] = meeting_results
            all_metrics.append(meeting_results)
            
            print(f"   ✅ Tasks: GT={meeting_results['ground_truth_tasks']}, AI={meeting_results['ai_predicted_tasks']}")
            print(f"   📈 F1: {meeting_results['task_f1']}, Precision: {meeting_results['task_precision']}, Recall: {meeting_results['task_recall']}")
            print(f"   👤 Owner Accuracy: {meeting_results['owner_accuracy']}")
            print(f"   ⚡ Priority Accuracy: {meeting_results['priority_accuracy']}")
    
    # Calculate overall averages
    if all_metrics:
        overall = {
            'avg_task_f1': round(sum(m['task_f1'] for m in all_metrics) / len(all_metrics), 3),
            'avg_task_precision': round(sum(m['task_precision'] for m in all_metrics) / len(all_metrics), 3),
            'avg_task_recall': round(sum(m['task_recall'] for m in all_metrics) / len(all_metrics), 3),
            'avg_owner_accuracy': round(sum(m['owner_accuracy'] for m in all_metrics) / len(all_metrics), 3),
            'avg_priority_accuracy': round(sum(m['priority_accuracy'] for m in all_metrics) / len(all_metrics), 3),
            'total_meetings_evaluated': len(all_metrics)
        }
    else:
        overall = {"error": "No successful evaluations"}
    
    results['overall'] = overall
    
    return results

def print_evaluation_summary(results: Dict[str, Any]) -> None:
    """
    Print a clean summary of evaluation results.
    """
    print("\n" + "="*60)
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    
    if 'overall' in results and 'error' not in results['overall']:
        overall = results['overall']
        print(f"📈 OVERALL METRICS (across {overall['total_meetings_evaluated']} meetings):")
        print(f"   Task F1 Score:       {overall['avg_task_f1']}")
        print(f"   Task Precision:      {overall['avg_task_precision']}")
        print(f"   Task Recall:         {overall['avg_task_recall']}")
        print(f"   Owner Accuracy:      {overall['avg_owner_accuracy']}")
        print(f"   Priority Accuracy:   {overall['avg_priority_accuracy']}")
        
        print(f"\n🎯 COMPETITION TARGETS:")
        print(f"   Target F1 ≥ 0.75:    {'✅ ACHIEVED' if overall['avg_task_f1'] >= 0.75 else '❌ NEEDS WORK'}")
        print(f"   Target Owner Acc ≥ 0.8: {'✅ ACHIEVED' if overall['avg_owner_accuracy'] >= 0.8 else '❌ NEEDS WORK'}")
    
    # Print per-meeting details
    print(f"\n📋 PER-MEETING RESULTS:")
    for meeting_id, metrics in results.items():
        if meeting_id != 'overall' and 'error' not in metrics:
            print(f"   {meeting_id}: F1={metrics['task_f1']}, Owner Acc={metrics['owner_accuracy']}")