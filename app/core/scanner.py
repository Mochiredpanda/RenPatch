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
def analyze_font_role(base_dir, font_path):
    """
    Heuristics to determine the role of a font (Dialogue, UI, unknown).
    Scans `gui.rpy` if available.
    """
    font_filename = os.path.basename(font_path)
    role = "Unknown"
    confidence = "Low"

    # Check file path conventions
    if "gui" in font_path.lower() or "interface" in font_path.lower():
        role = "UI"
        confidence = "Medium"
    if "game" in font_path.lower() and "fonts" not in font_path.lower():
         # Often fonts in root game dir are used for dialogue if custom
         pass

    # Check gui.rpy definitions
    # Look for gui.text_font = "..." and gui.interface_text_font = "..."
    # This is a robust check.
    gui_rpy_path = None
    for root, _, files in os.walk(base_dir):
        if "gui.rpy" in files:
            gui_rpy_path = os.path.join(root, "gui.rpy")
            break
            
    if gui_rpy_path:
        try:
            with open(gui_rpy_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for Dialogue Font
                # gui.text_font = "gui/font/SourceHanSansLite.ttf"
                if re.search(f'gui\.text_font\s*=\s*[\'"].*{re.escape(font_filename)}[\'"]', content):
                    return "Dialogue", "High"
                
                # Check for Interface Font
                if re.search(f'gui\.interface_text_font\s*=\s*[\'"].*{re.escape(font_filename)}[\'"]', content):
                    return "UI", "High"
                
                # Check for Name Font (often same as Interface or Dialogue)
                if re.search(f'gui\.name_text_font\s*=\s*[\'"].*{re.escape(font_filename)}[\'"]', content):
                     return "Name/UI", "Medium"

        except Exception as e:
            print(f"Error reading gui.rpy: {e}")

    return role, confidence
