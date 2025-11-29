# app.py - Simple Cloud Run compatible API
from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv

# Add src to Python path
sys.path.append('/app/src')

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        "status": "Meeting Execution Agent API is running!",
        "version": "1.0",
        "endpoints": {
            "health": "GET /",
            "analyze": "POST /analyze"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_meeting():
    """
    Cloud API endpoint for meeting analysis
    """
    try:
        data = request.json
        if not data or 'transcript' not in data:
            return jsonify({"success": False, "error": "Missing 'transcript' in request body"}), 400
        
        transcript = data.get('transcript', '')
        
        if not transcript.strip():
            return jsonify({"success": False, "error": "Transcript cannot be empty"}), 400
        
        # Import and use our pipeline
        try:
            from src.ingest import process_transcript_from_text
            from src.understand import analyze_meeting
            from src.validate import validate_tasks, deduplicate_tasks
            from src.planner import plan_tasks
        except ImportError as e:
            return jsonify({"success": False, "error": f"Module import error: {str(e)}"}), 500
        
        # Run the pipeline
        try:
            analysis_results = analyze_meeting(transcript)
            tasks = analysis_results.get('tasks', [])
            participants = analysis_results.get('participants', [])
            
            validated_tasks = validate_tasks(tasks, participants)
            deduplicated_tasks = deduplicate_tasks(validated_tasks)
            planned_tasks = plan_tasks(deduplicated_tasks)
            
            return jsonify({
                "success": True,
                "tasks": planned_tasks,
                "meeting_summary": analysis_results.get('meeting_summary', ''),
                "decisions": analysis_results.get('decisions', []),
                "participants": participants,
                "total_tasks": len(planned_tasks)
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": f"Pipeline execution error: {str(e)}"}), 500
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "meeting-execution-agent"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)