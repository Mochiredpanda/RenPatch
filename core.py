import os
import re

from fontTools.ttLib import TTFont

### SCANNER ###
def get_unique_characters(game_dir):
    """
    Scan and extract all special chars from .rpy files in the game directory.
    Return: a set of unique characters in the game.
    """
    unique_chars = set()
    
    # Regex search:
    # 1. For all content inside double or single quotes.
    # 2. Skip non-script common file paths (images/, audio/, music/, gui/, fonts/, etc.)
    # TODO: Refine the scanner logic later.
    pattern = re.compile(r'["\'](?!images/|audio/|music/|gui/|fonts/)(.*?)["\']')

    for root, _, files in os.walk(game_dir):
        for file in files:
            if file.endswith(".rpy"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Find all strings
                        matches = pattern.findall(content)
                        for text in matches:
                            for char in text:
                                # Ignore whitespace and control characters
                                if not char.isspace():
                                    unique_chars.add(char)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return unique_chars

### TOFU EXTRACTOR ###
def get_missing_characters(found_chars, lite_font_path):
    """
    Identifies characters in found_chars but missing from the lite_font.
    Return: a set of diff / missing characters.
    """
    missing_chars = set()
    
    try:
        # Load the Lite font (Set: A)
        font = TTFont(lite_font_path)
        
        # Get cmap table
        unicode_map = font.getBestCmap() 
        
        # unicode_map
        # keys: Unicode ordinals (int)
        # values: glyph names
        
        for char in found_chars:
            # use ord() to convert character to its Unicode int ID
            if ord(char) not in unicode_map:
                missing_chars.add(char)
                
        font.close()
        
    except Exception as e:
        print(f"Error analyzing font {lite_font_path}: {e}")
        
    return missing_chars