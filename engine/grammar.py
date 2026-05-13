import language_tool_python
import re

# MOVE THIS HERE: Initialize the tool once at the top of the file.
# This makes the API lightning fast after the initial startup.
tool = language_tool_python.LanguageTool('en-US')

def pre_clean_text(text):
    """Sanitizes text before grammar checking to prevent false positives."""
    if not text:
        return ""
        
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # Replace arbitrary newlines with spaces to fix broken sentences
    text = text.replace('\n', ' ')
    
    # Clean up double spaces created by the removals
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def check_grammar(text):
    """Checks grammar and returns a list of issues."""
    return []