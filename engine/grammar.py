import language_tool_python
import re

# 🌟 THE FIX: Point to the public API to avoid requiring Java on the server
tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org/v2')

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
    
    # Logic: Use the global 'tool' variable which now connects to the public API
    try:
        matches = tool.check(clean_txt)
    except Exception as e:
        print(f"Grammar check failed: {e}")
        return []
    
    errors = []
    # Filter out spellings (jargon), title cases, and minor typos
    ignore_rules = ["MORFOLOGIK_RULE_EN_US", "UPPERCASE_SENTENCE_START", "POSSIBLE_TYPO"]
    
    for match in matches:
        rule_id = getattr(match, 'ruleId', getattr(match, 'rule_id', 'Unknown'))
        
        if any(rule in rule_id for rule in ignore_rules):
            continue
            
        errors.append({
            "message": match.message,
            "context": match.context,
            "suggestion": match.replacements[0] if match.replacements else "N/A"
        })
        
        # Limit to 5 errors to keep the UI clean
        if len(errors) >= 5:
            break
            
    return errors # 🌟 FIXED: Returned 'errors' list instead of an empty list