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

# Surgical Subsetter to find missing chars in a substitute font
def generate_patch_font(missing_chars, full_font_path, output_path):
    """
    Extracts specific characters from a full font and saves them as a tiny subset font.
    Return: Bool
    """
    if not missing_chars:
        return True, 0.0, set()

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
            print("\nThe following characters do not exist in your donor font.")
            print(f"Failed to patch: \n{''.join(list(failed))}")
            print("Try with another donor font.")
        
        return True, rate, failed

    except Exception as e:
        print(f"Error generating patch font: {e}")
        return False, 0.0, missing_chars
    
### FONT PACTCH SCRIPT ###
# TODO: Fix output script to only includes successfully patched missing characters.
def generate_renpy_script(missing_chars, patch_filename, lite_font_filename, output_path):
    """
    Creates a drop-in .rpy script with explicit character mapping for every missing glyph.
    """
    if not missing_chars:
        return False
    
    script_lines = [
        "# --- RenPatch Auto-Generated Integration ---",
        f"# Missing Characters Handled: {len(missing_chars)}",
        "",
        "init python:",
        "    # Initialize the FontGroup",
        "    renpatch_font = FontGroup()"
    ]
    
    # Add explicit surgical entries for every missing character
    # Sort by ordinal to keep it organized
    sorted_missing = sorted(list(missing_chars), key=lambda x: ord(x))
    
    script_lines.append("    # Explicitly map missing characters to the patch font")
    for char in sorted_missing:
        hex_code = hex(ord(char))
        # Represent the char in a comment for developer readability
        script_lines.append(f"    renpatch_font = renpatch_font.add('{patch_filename}', {hex_code}, {hex_code}) # {char}")

    # 3. Add the Lite font as the final fallback for everything else
    script_lines.append("")
    script_lines.append("    # Use Lite font for all the other characters")
    script_lines.append(f"    renpatch_font = renpatch_font.add('{lite_font_filename}', 0x0000, 0xffff)")
    
    # 4. Map the group to the config
    script_lines.append("")
    script_lines.append('    # Map the group to "renpatch_style" for use')
    script_lines.append("    # Rename your font group name to replace 'renpatch_style' if needed.")
    script_lines.append("    # Make sure to keep your front group name IN the single quotes.")
    script_lines.append("    config.font_name_map['renpatch_style'] = renpatch_font")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(script_lines))
        print(f"Integration script generated with {len(missing_chars)} explicit mappings.")
        return True
    except Exception as e:
        print(f"Error generating Ren'Py script: {e}")
        return False