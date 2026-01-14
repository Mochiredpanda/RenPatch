# RenPatch Patcher Module
import os
import json
import unicodedata
from fontTools.ttLib import TTFont
from fontTools import subset

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
    
### MULTI-SOURCE PATCHING ###

def generate_multi_patch(missing_chars, donor_paths, output_dir):
    """
    Tries to find missing characters across a prioritized list of donor fonts.
    Generates one subset font per donor if used.
    
    Returns:
        patches_info (list): [{ "filename": "patch_0.ttf", "chars": set(...) }, ...]
        failed_chars (set): Chars not found in any donor.
    """
    if not missing_chars:
        return [], set()

    remaining_chars = set(missing_chars)
    patches_info = []
    
    print(f"\n--- Starting Multi-Patch Generation ({len(donor_paths)} donors) ---")

    for i, donor_path in enumerate(donor_paths):
        if not remaining_chars:
            break
            
        print(f"Checking donor {i+1}: {os.path.basename(donor_path)}...")
        
        try:
            # 1. Check which needed chars are in this donor
            font = TTFont(donor_path)
            cmap = font.getBestCmap() # Unicode map
            
            chars_found_in_donor = set()
            for char in remaining_chars:
                if ord(char) in cmap:
                    chars_found_in_donor.add(char)
            font.close()
            
            if not chars_found_in_donor:
                print("  No useful characters found.")
                continue
                
            # 2. Generate a subset for these characters
            patch_filename = f"patch_{i}.ttf"
            output_path = os.path.join(output_dir, patch_filename)
            
            # Using the existing single-font generator logic, but specifying exact chars
            # We call the subsetter directly to avoid redundancy
            
            options = subset.Options()
            options.notdef_outline = True
            
            donor_font = TTFont(donor_path)
            subsetter = subset.Subsetter(options=options)
            text_to_extract = "".join(list(chars_found_in_donor))
            subsetter.populate(text=text_to_extract)
            subsetter.subset(donor_font)
            donor_font.save(output_path)
            donor_font.close()
            
            # 3. Verify
            success, failed_verify = verify_patch(chars_found_in_donor, output_path)
            
            print(f"  Generated {patch_filename} with {len(success)} chars.")
            
            if success:
                patches_info.append({
                    "filename": patch_filename,
                    "chars": success,
                    "source": os.path.basename(donor_path)
                })
                # Update remaining
                remaining_chars -= success
                
        except Exception as e:
            print(f"Error processing donor {donor_path}: {e}")
            continue

    return patches_info, remaining_chars

### FONT PACTCH SCRIPT ###

def generate_renpy_script(patches_list, failed_chars, lite_font_filename, output_path, log_path=None):
    """
    Creates a drop-in .rpy script.
    
    patches_list: List of dicts, each containing:
      - filename: "patch_0.ttf"
      - chars: set of characters
      - source: "SourceHanSans.otf" (optional metadata)
    
    failed_chars: Set of characters that couldn't be patched.
    """
    
    success_count = sum(len(p['chars']) for p in patches_list)
    total_needed = success_count + len(failed_chars)
    
    if total_needed == 0:
        return False
    
    ## Generate Log File ##
    if log_path:
        log_patches = []
        for p in patches_list:
            char_data = []
            for char in sorted(list(p['chars']), key=lambda x: ord(x)):
                char_data.append({
                    "char": char,
                    "hex": f"U+{ord(char):04X}",
                    "name": unicodedata.name(char, "Unknown")
                })
            log_patches.append({
                "filename": p['filename'],
                "source": p.get('source', 'Unknown'),
                "chars": char_data
            })

        failed_data = []
        for char in sorted(list(failed_chars), key=lambda x: ord(x)):
            failed_data.append({
                "char": char,
                "hex": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "Unknown")
            })

        log_data = {
            "patches": log_patches,
            "failed": failed_data,
            "lite_font_filename": lite_font_filename,
            "summary": {
                "patched": success_count,
                "failed": len(failed_chars)
            }
        }
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=4)
            print(f"Log generated: {log_path}")
        except Exception as e:
            print(f"Error generating log file: {e}")

    ## Generate Script ##
    script_lines = [
        "# --- RenPatch Auto-Generated Integration ---",
        f"# Patched Characters: {success_count}",
        f"# Failed Characters: {len(failed_chars)}",
        "",
        "init python:",
        "    # Initialize the FontGroup",
        "    renpatch_font = FontGroup()"
    ]
    
    # 1. Add Patches
    if patches_list:
        script_lines.append("")
        script_lines.append("    # --- Patch Fonts ---")

        for patch in patches_list:
            filename = patch['filename']
            source = patch.get('source', '')
            chars = sorted(list(patch['chars']), key=lambda x: ord(x))
            
            script_lines.append(f"    # From: {source} ({len(chars)} chars)")
            
            for char in chars:
                hex_code_py = hex(ord(char))
                hex_code_display = f"U+{ord(char):04X}"
                # Add individual char mapping
                script_lines.append(f"    renpatch_font = renpatch_font.add('{filename}', {hex_code_py}, {hex_code_py}) # {char} ({hex_code_display})")
            
            script_lines.append("")
    
    # 2. Add Failed Chars Comments
    if failed_chars:
        script_lines.append("    # === FAILED TO PATCH CHARACTERS ===")
        script_lines.append("    # The following characters were NOT found in any donor fonts.")
        
        sorted_failed = sorted(list(failed_chars), key=lambda x: ord(x))
        for char in sorted_failed:
            hex_code = f"U+{ord(char):04X}"
            try:
                name = unicodedata.name(char)
            except ValueError:
                name = "Unknown"
            script_lines.append(f"    # FAILED: {char} ({hex_code}) - {name}")

    # 3. Fallback to Lite Font
    script_lines.append("")
    script_lines.append("    # Use Lite font for all the other characters")
    script_lines.append(f"    renpatch_font = renpatch_font.add('{lite_font_filename}', 0x0000, 0xffff)")
    
    # 4. Config Map
    script_lines.append("")
    script_lines.append('    # Map the group to "renpatch_style" for use')
    script_lines.append("    config.font_name_map['renpatch_style'] = renpatch_font")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(script_lines))
        print(f"\nIntegration script generated at {output_path}")
        return True
    except Exception as e:
        print(f"Error generating Ren'Py script: {e}")
        return False
