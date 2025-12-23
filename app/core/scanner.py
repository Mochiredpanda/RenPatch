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
