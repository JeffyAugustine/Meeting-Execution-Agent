# src/understand.py
from typing import List, Dict, Any
from .gemini_client import extract_tasks_from_transcript

def analyze_meeting(transcript: str, api_key: str = None) -> Dict[str, Any]:
    """
    Main function to analyze meeting transcript and extract structured information.
    
    Args:
        transcript (str): The meeting transcript
        api_key (str): Google AI Studio API key
        
    Returns:
        Dict[str, Any]: Structured analysis results
    """
    # Setup Gemini (will use environment variable if api_key is None)
    from .gemini_client import setup_gemini
    setup_gemini(api_key)
    
    # Extract tasks and meeting insights
    results = extract_tasks_from_transcript(transcript)
    
    return results

def print_analysis_results(results: Dict[str, Any]) -> None:
    """
    Pretty print the analysis results.
    
    Args:
        results (Dict[str, Any]): Analysis results from analyze_meeting
    """
    print("📊 MEETING ANALYSIS RESULTS")
    print("=" * 60)
    
    # Meeting Summary
    print(f"\n📋 MEETING SUMMARY:")
    print(f"   {results.get('meeting_summary', 'No summary generated')}")
    
    # Decisions
    decisions = results.get('decisions', [])
    print(f"\n✅ KEY DECISIONS ({len(decisions)}):")
    for i, decision in enumerate(decisions, 1):
        print(f"   {i}. {decision}")
    
    # Participants
    participants = results.get('participants', [])
    print(f"\n👥 PARTICIPANTS ({len(participants)}):")
    for participant in participants:
        print(f"   • {participant}")
    
    # Tasks
    tasks = results.get('tasks', [])
    print(f"\n🎯 ACTIONABLE TASKS ({len(tasks)}):")
    print("-" * 40)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task.get('title', 'No title')}")
        print(f"   📝 Description: {task.get('description', 'No description')}")
        print(f"   👤 Owner: {task.get('owner', 'TBD')}")
        print(f"   📅 Deadline: {task.get('deadline', 'TBD')}")
        print(f"   ⚡ Priority: {task.get('priority', 'Medium')}")
        print(f"   🎯 Confidence: {task.get('confidence', 0.0):.2f}")
        print(f"   🔍 Evidence: '{task.get('evidence', 'No evidence')}'")