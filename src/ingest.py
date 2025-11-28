# src/ingest.py

def load_transcript(file_path: str) -> str:
    """
    Load transcript from a text file.
    
    Args:
        file_path (str): Path to the transcript file
        
    Returns:
        str: Raw transcript content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error loading transcript from {file_path}: {e}")
        return ""

def clean_transcript(raw_text: str) -> str:
    """
    Basic cleaning of transcript text.
    
    Args:
        raw_text (str): Raw transcript text
        
    Returns:
        str: Cleaned transcript text
    """
    # Remove excessive whitespace but preserve speaker formatting
    import re
    cleaned = re.sub(r'\n\s*\n', '\n\n', raw_text)  # Multiple newlines to double newline
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Multiple spaces/tabs to single space
    return cleaned.strip()

def process_transcript(file_path: str) -> str:
    """
    Main function to process a transcript file.
    
    Args:
        file_path (str): Path to the transcript file
        
    Returns:
        str: Processed transcript content
    """
    raw_text = load_transcript(file_path)
    cleaned_text = clean_transcript(raw_text)
    return cleaned_text

# Example usage
if __name__ == "__main__":
    sample_text = process_transcript("../data/sample_transcripts/meeting_01.txt")
    print(f"Processed transcript length: {len(sample_text)} characters")
    print("First 500 characters:")
    print(sample_text[:500])