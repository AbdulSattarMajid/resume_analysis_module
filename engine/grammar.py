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
    """Step 4: Professional Grammar Check (No Jargon Flags)"""
    clean_txt = pre_clean_text(text)
    
    # Logic: Use the global 'tool' variable instead of creating a new one
    matches = tool.check(clean_txt)
    
    errors = []
    # Filter out spellings (jargon), title cases, and minor typos
    ignore_rules = ["MORFOLOGIK_RULE_EN_US", "UPPERCASE_SENTENCE_START", "POSSIBLE_TYPO"]
    
    for match in matches:
        # FIXED: Use 'ruleId' (camelCase) to avoid AttributeErrors
        # We use getattr as a safety net in case of version drift
        rule_id = getattr(match, 'ruleId', getattr(match, 'rule_id', 'Unknown'))
        
        if any(rule in rule_id for rule in ignore_rules):
            continue
            
        errors.append({
            "message": match.message,
            "context": match.context,
            "suggestion": match.replacements[0] if match.replacements else "N/A"
        })
        
        # Limit to 5 errors to keep the UI clean for the React frontend
        if len(errors) >= 5:
            break
            
    return []