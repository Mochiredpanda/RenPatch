import os
import re

from fontTools.ttLib import TTFont
from fontTools import subset

import unicodedata

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
# Extract missing chars in lite font
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
        # Use getBestCmap() to get most comprehensive Unicode-compatible table
        unicode_map = font.getBestCmap() 
        
        # unicode_map
        # keys: Unicode ordinals (int)
        # values: glyph names
        
        for char in found_chars:
            # use ord() to convert character to its Unicode int ID
            # O(1)
            if ord(char) not in unicode_map:
                missing_chars.add(char)
                
        font.close()
             
    except Exception as e:
        print(f"Error analyzing font {lite_font_path}: {e}")
        
    return missing_chars

# Generate Report of Tofu Characters
def save_missing_report(missing_chars, report_path, font_name):
    """
    Generates a Markdown report of missing characters with hex codes and wiki links.
    """
    if not missing_chars:
        return

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RenPatch: Missing Characters Report\n\n")
        f.write("The following characters were found in your scripts but are missing from your font %s.\n\n" % font_name)
        f.write("| Char | Hex Code | Unicode Name | Wiki Link |\n")

        # Sort by hex code
        sorted_chars = sorted(list(missing_chars), key=lambda x: ord(x))

        for char in sorted_chars:
            hex_code = f"{ord(char):04X}"
            
            # Get a human-readable name
            #   e.g., "CJK UNIFIED IDEOGRAPH-561A"
            try:
                name = unicodedata.name(char)
            except ValueError:
                name = "Unknown Character"

            # Compart links
            wiki_link = f"[View on Compart](https://www.compart.com/en/unicode/U+{hex_code})"
            
            f.write(f"{char}\tU+{hex_code}\t{name}\t{wiki_link}\n")

    print(f"Report generated: {report_path}")

### SUBSETTER ###
# Surgical Subsetter to find missing chars in a substitute font

def generate_patch_font(missing_chars, full_font_path, output_path):
    """
    Extracts specific characters from a full font and saves them as a tiny subset font.
    Return: Bool, T for patch font file generated successfully.
    """
    if not missing_chars:
        print("No missing characters found. No patch needed!")
        return False

    try:
        # Config subsetter options
        # default options, optimized for size
        options = subset.Options()
        
        # Prepare set to list
        text_to_extract = "".join(list(missing_chars))
        
        # Load full font and do subsetting
        font = TTFont(full_font_path)
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=text_to_extract)
        subsetter.subset(font)
        
        # Save patch font
        font.save(output_path)
        font.close()
        
        print(f"Success! Patch font saved to: {output_path}")
        print(f"Patch size: {os.path.getsize(output_path) / 1024:.2f} KB")
        return True

    except Exception as e:
        print(f"Error generating patch font: {e}")
        return False