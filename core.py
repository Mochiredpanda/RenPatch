# RenPatch: A tool to patch missing characters in Ren'Py scripts.
# Author: Mochiredpanda/Jiyuhe
# Version: 0.2
# License: MIT

import os
import re
import json

from fontTools.ttLib import TTFont
from fontTools import subset

import unicodedata

### SCANNER ###
# 0.2: Optimized with Extract-Filter-Clean pipeline
# 0.1: Using Naive guess-and-check
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

### EXTRACTOR ###
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

# Generate Report of Missing Characters
def save_missing_report(missing_chars, font_name, output_dir="."):
    """
    Generates a JSON report of missing characters in the specified directory.
    Default: 'missing_characters_report.json' in current directory.
    """
    if not missing_chars:
        return

    # Prepare data structure
    json_data = []
    sorted_chars = sorted(list(missing_chars), key=lambda x: ord(x))

    for char in sorted_chars:
        hex_code = f"U+{ord(char):04X}"
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = "Unknown Character"

        wiki_link = f"https://www.compart.com/en/unicode/{hex_code}"
        
        json_data.append({
            "char": char,
            "hex": hex_code,
            "name": name,
            "wiki_link": wiki_link
        })

    # Save to JSON
    output_path = os.path.join(output_dir, "missing_characters_report.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print(f"Missing characters report generated: {output_path}")
    except Exception as e:
        print(f"Error generating missing report: {e}")

### SUBSETTER ###

# Verify patch result to missing char set
def verify_patch(target_chars, patch_path):
    """
    Checks the generated patch to see which characters actually made it in.
    Return: sets of success and failed characters.
    """
    if not os.path.exists(patch_path):
        return set()

    patch_font = TTFont(patch_path)
    patch_cmap = patch_font.getBestCmap()
    patch_font.close()

    # Characters that are successfully in the patch
    success_chars = {c for c in target_chars if ord(c) in patch_cmap}
    failed_chars = target_chars - success_chars

    return success_chars, failed_chars

# Subsetter to find missing chars in a substitute font
def generate_patch_font(missing_chars, full_font_path, output_path):
    """
    Extracts specific characters from a full font and saves them as a tiny subset font.
    Return: Bool, success chars, failed chars
    """
    if not missing_chars:
        return True, set(), set()

    try:
        # Config subsetter options
        options = subset.Options()
        # Keep glyph names
        options.notdef_outline = True
        
        # Load full font and do subsetting
        font = TTFont(full_font_path)
        subsetter = subset.Subsetter(options=options)
        text_to_extract = "".join(list(missing_chars)) # conver to list
        subsetter.populate(text=text_to_extract)
        subsetter.subset(font)
        
        # Save patch font
        font.save(output_path)
        font.close()
        
        # --- Verification Report ---
        success, failed = verify_patch(missing_chars, output_path)
        total = len(missing_chars)
        rate = (len(success) / total) * 100 if total > 0 else 100
        
        print(f"\n--- Patch Report ---")
        print(f"Success! Patch font saved to: {output_path}")
        print(f"Patch size: {os.path.getsize(output_path) / 1024:.2f} KB")
        print(f"Patch Rate: {rate:.2f}% ({len(success)} out of {total})")
        
        if failed:
            print(f"\n--- Failed Patch ---")
            print("The following characters do not exist in your donor font.")
            print(f"Failed to patch: \n{''.join(list(failed))}")
            print("Try with another donor font.")
        
        return True, success, failed

    except Exception as e:
        print(f"Error generating patch font: {e}")
        return False, set(), missing_chars
    
### FONT PACTCH SCRIPT ###
def generate_renpy_script(success_chars, failed_chars, patch_filename, lite_font_filename, output_path, log_path=None):
    """
    Creates a drop-in .rpy script with explicit character mapping for every missing glyph.
    Generates a JSON log for the GUI version.
    """
    if not success_chars and not failed_chars:
        return False
    
    ## Generate Log File ##
    if log_path:
        # Create rich data objects
        success_data = []
        for char in sorted(list(success_chars), key=lambda x: ord(x)):
            success_data.append({
                "char": char,
                "hex": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "Unknown")
            })
            
        failed_data = []
        for char in sorted(list(failed_chars), key=lambda x: ord(x)):
            failed_data.append({
                "char": char,
                "hex": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "Unknown")
            })

        log_data = {
            "success": success_data,
            "failed": failed_data,
            "patch_filename": patch_filename,
            "lite_font_filename": lite_font_filename
        }
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=4)
            print("\n--- Patch Log ---")
            print(f"Log generated: {log_path}")
        except Exception as e:
            print(f"Error generating log file: {e}")

    ## Generate Script ##
    script_lines = [
        "# --- RenPatch Auto-Generated Integration ---",
        f"# Patched Characters: {len(success_chars)}",
        f"# Failed Characters: {len(failed_chars)}",
        "",
        "init python:",
        "    # Initialize the FontGroup",
        "    renpatch_font = FontGroup()"
    ]
    
    # Add explicit surgical entries for all SUCCESSFUL characters
    sorted_success = sorted(list(success_chars), key=lambda x: ord(x))
    
    script_lines.append("")
    script_lines.append("    # Explicitly map successfully patched font")
    for char in sorted_success:
        hex_code_py = hex(ord(char))
        hex_code_display = f"U+{ord(char):04X}"
        script_lines.append(f"    renpatch_font = renpatch_font.add('{patch_filename}', {hex_code_py}, {hex_code_py}) # {char} ({hex_code_display})")

    # Add comments for FAILED characters
    if failed_chars:
        script_lines.append("")
        script_lines.append("    # === FAILED TO PATCH CHARACTERS ===")
        script_lines.append("    # The following characters were NOT found in the donor font.")
        script_lines.append("    # You may need to find another donor font or handle them manually.")
        
        sorted_failed = sorted(list(failed_chars), key=lambda x: ord(x))
        for char in sorted_failed:
            hex_code = f"U+{ord(char):04X}"
            try:
                name = unicodedata.name(char)
            except ValueError:
                name = "Unknown"
            script_lines.append(f"    # FAILED: {char} ({hex_code}) - {name}")

    # Add the Lite font as the final fallback for everything else
    script_lines.append("")
    script_lines.append("    # Use Lite font for all the other characters")
    script_lines.append(f"    renpatch_font = renpatch_font.add('{lite_font_filename}', 0x0000, 0xffff)")
    
    # Map the group to the config
    script_lines.append("")
    script_lines.append('    # Map the group to "renpatch_style" for use')
    script_lines.append("    # Rename your font group name to replace 'renpatch_style' if needed.")
    script_lines.append("    # Make sure to keep your font group name IN the single quotes.")
    script_lines.append("    config.font_name_map['renpatch_style'] = renpatch_font")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(script_lines))
        print(f"\nIntegration script generated with {len(success_chars)} out of {len(success_chars) + len(failed_chars)} explicit mappings.")
        return True
    except Exception as e:
        print(f"Error generating Ren'Py script: {e}")
        return False