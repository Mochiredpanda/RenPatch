# RenPatch Scanner Module
import os
import re

def get_unique_characters(game_dir):
    """
    Scan and extract all special chars from .rpy files in the game directory.
    Return: a set of unique characters in the game.
    """
    unique_chars = set()
    
    # Single pass extraction
    # 1. Capture triple-quoted strings first (Greedy)
    # 2. Capture single/double quoted strings with backslash escape support
    # Pattern explanation for " or ':
    #   "          : Start quote
    #   (          : Capture group
    #     [^"\\]*  : Match any char except quote or backslash (Greedy)
    #     (?:      : Non-capturing group for escaped char
    #       \\.    : Match backslash followed by any char
    #       [^"\\]* : Match any char except quote or backslash
    #     )*       : Repeat 0 or more times
    #   )          : End capture
    #   "          : End quote
    string_pattern = re.compile(r'("""(.*?)"""|\'\'\'(.*?)\'\'\'|"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\')', re.DOTALL)
    
    # Ren'Py specific strip
    tag_pattern = re.compile(r'\{.*?\}') # patterns like {size=30}, {b}, etc. 
    interpolation_pattern = re.compile(r'\[.*?\]') # patterns like [player_name]

    # Heuristic pre-filtering
    ignored_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.ogg', '.mp3', '.wav', '.rpy', '.otf', '.ttf')

    for root, _, files in os.walk(game_dir):
        for file in files:
            if file.endswith(".rpy"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        matches = string_pattern.findall(content)
                        
                        for match_tuple in matches:
                            # The match tuple contains full match + groups. 
                            # We want the content inside the quotes.
                            # Groups: 
                            # 0: Full match ("""...""" or "...")
                            # 1: content of """..."""
                            # 2: content of '''...'''
                            # 3: content of "..."
                            # 4: content of '...'
                            
                            # Find the non-empty group (skip group 0)
                            text = next((m for m in match_tuple[1:] if m), None)
                            
                            if not text:
                                continue
                                
                            # Skip likely file paths
                            if text.lower().strip().endswith(ignored_extensions):
                                continue
                            if "/" in text and len(text.split()) == 1: # Single word with slash likely a path
                                continue

                            # Clean up the text
                            # Strip Ren'Py tags
                            text = tag_pattern.sub('', text)
                            # Strip Interpolation
                            text = interpolation_pattern.sub('', text)
                            # Common escape sequences
                            text = text.replace('\\"', '"').replace("\\'", "'").replace("\\n", "")
                            
                            for char in text:
                                # Ignore whitespace and control characters
                                if not char.isspace() and char.isprintable():
                                    unique_chars.add(char)
                                    
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return unique_chars

def find_fonts(base_dir):
    """
    Recursively find all .ttf and .otf files in the directory.
    Returns a list of absolute paths.
    """
    font_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.ttf', '.otf')):
                font_files.append(os.path.join(root, file))
    return font_files

# Try to analyze font role based on file path and gui.rpy
def analyze_font_role(base_dir, font_path, missing_count=None, total_chars=0):
    """
    Heuristics to determine the role of a font (Dialogue, UI, unknown).
    1. Check gui.rpy/screens.rpy for explicit assignment.
    2. Check file path conventions.
    3. Check character coverage (if provided).
    """
    font_filename = os.path.basename(font_path)
    role = "Unknown"
    confidence = "Low"

    # 1. Check explicit definitions in common config files
    config_files = ["gui.rpy", "screens.rpy", "options.rpy"]
    found_config_match = False
    
    for config_file in config_files:
        if found_config_match: break
        
        # Find file in directory tree
        file_path = None
        for root, _, files in os.walk(base_dir):
            if config_file in files:
                file_path = os.path.join(root, config_file)
                break
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Regex Pattern to catch:
                    # gui.text_font = "path/to/font.ttf"
                    # font "path/to/font.ttf"
                    escaped_name = re.escape(font_filename)
                    
                    # High Priority: Dialogue assignments
                    if re.search(f'gui\.text_font\s*=\s*[\'"].*{escaped_name}[\'"]', content):
                        role = "Dialogue"
                        confidence = "High"
                        found_config_match = True
                        break
                        
                    # Medium Priority: UI assignments
                    if re.search(f'gui\.interface_text_font\s*=\s*[\'"].*{escaped_name}[\'"]', content) or \
                       re.search(f'gui\.name_text_font\s*=\s*[\'"].*{escaped_name}[\'"]', content) or \
                       re.search(f'font\s+[\'"].*{escaped_name}[\'"]', content): # General style font
                        role = "UI"
                        confidence = "Medium"
                        found_config_match = True
                        break
            except:
                pass

    if found_config_match:
        return role, confidence

    # 2. Check file path conventions (Fallback)
    if "gui" in font_path.lower() or "interface" in font_path.lower() or "common" in font_path.lower():
        role = "UI"
        confidence = "Medium"
    
    # 3. Coverage Heuristic (Fallback if still Unknown)
    if role == "Unknown" and missing_count is not None and total_chars > 0:
        coverage = (total_chars - missing_count) / total_chars
        
        if coverage > 0.8: 
            # If it covers >80% of unique chars, it's likely a primary dialogue font
            role = "Dialogue"
            confidence = "Low" 
        elif coverage < 0.1:
            # Very low coverage usually implies symbols or very specific UI font
            role = "UI/Symbols"
            confidence = "Low"

    return role, confidence
