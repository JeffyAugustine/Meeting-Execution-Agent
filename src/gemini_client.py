# src/gemini_client.py
import google.generativeai as genai
import os
import json
from typing import Dict, Any

def setup_gemini(api_key: str = None) -> None:
    """
    Setup Google Gemini API.
    
    Args:
        api_key (str): Your Google AI Studio API key. If None, will look for GOOGLE_API_KEY env variable.
    """
    if api_key is None:
        api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        raise ValueError("Please provide a Google AI Studio API key or set GOOGLE_API_KEY environment variable")
    
    genai.configure(api_key=api_key)

def extract_tasks_from_transcript(transcript: str, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    Extract tasks from meeting transcript using Gemini.
    
    Args:
        transcript (str): The meeting transcript
        model_name (str): Gemini model to use
        
    Returns:
        Dict[str, Any]: Structured task extraction results
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel(model_name)
        
        # System prompt for task extraction
        system_prompt = """
        You are an expert meeting assistant specialized in extracting actionable tasks from meeting transcripts.
        Extract EVERY actionable task mentioned in the meeting, including owner, deadline, priority, and evidence.

        CRITICAL: Return ONLY valid JSON. No other text.

        JSON Format:
        {
            "tasks": [
                {
                    "title": "Short, actionable task title",
                    "description": "Detailed description of what needs to be done",
                    "owner": "Name of person responsible (extract from transcript)",
                    "deadline": "Specific deadline mentioned (e.g., 'next Friday', 'EOD tomorrow') or 'TBD'",
                    "priority": "High/Medium/Low (infer from context)",
                    "confidence": 0.0-1.0 (your confidence in this extraction),
                    "evidence": "Exact quote from transcript that led to this task"
                }
            ],
            "meeting_summary": "1-2 sentence summary of key decisions and outcomes",
            "decisions": ["List of key decisions made", "Another decision"],
            "participants": ["List of all participant names mentioned"]
        }

        Guidelines:
        - Only extract concrete, actionable tasks
        - If no clear owner, use "TBD"
        - If no deadline, use "TBD" 
        - Base priority on urgency language and importance to meeting goals
        - Confidence should reflect certainty in owner, deadline, and task clarity
        """
        
        user_prompt = f"""
        MEETING TRANSCRIPT:
        {transcript}

        Extract all actionable tasks and meeting outcomes.
        """
        
        # Generate response
        response = model.generate_content([system_prompt, user_prompt])
        
        # Parse JSON response
        result_text = response.text.strip()
        
        # Clean the response (remove markdown code blocks if present)
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
            
        parsed_result = json.loads(result_text)
        return parsed_result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response.text}")
        return {"tasks": [], "meeting_summary": "", "decisions": [], "participants": []}
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"tasks": [], "meeting_summary": "", "decisions": [], "participants": []}