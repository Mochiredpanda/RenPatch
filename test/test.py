import os, sys
import re

from fontTools.ttLib import TTFont
from fontTools import subset

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from app.core import *

# --- Test Block ---
if __name__ == "__main__":
    # Test with game directory
    test_path = "/Users/jiyuhe/Downloads/game" 
    lite_font = "/Users/jiyuhe/Downloads/game/SourceHanSansLite.ttf"
    full_font = "/Users/jiyuhe/Downloads/game/NotoSansSC.ttf"
    donor_font = "/Users/jiyuhe/Downloads/game/DejaVuSans.ttf"

    patch_output = "/Users/jiyuhe/Downloads/game/patch.ttf"
    font_name = "SourceHanSansLite.ttf"
    rpy_output = "/Users/jiyuhe/Downloads/game/font_patch.rpy"
    
    if os.path.exists(test_path) and os.path.exists(lite_font) and os.path.exists(full_font):
        ## SCANNER TEST
        chars = get_unique_characters(test_path)
        print(f"Total unique characters found: {len(chars)}")
        # Print a sample
        print(f"Sample: {''.join(list(chars)[:20])}")

        # # Save found characters
        # txt_path = 'output_chars.txt'
        # with open(txt_path, 'w') as f:
        #     for i in range(0, len(chars), 20):
        #         chunk = list(chars)[i:i+20]
        #         f.write(' '.join(chunk) + '\n')
                
        ## EXTRACTOR TEST
        missing = get_missing_characters(chars, lite_font) 
        if missing:
            print(f"Total missing characters: {len(missing)}")
            print(f"Sample: {''.join(list(missing)[:20])}")
            # Generate Missing Report
            save_missing_report(missing, font_name)
            
            ## SUBSETTER TEST
            status, success, failed = generate_patch_font(missing, donor_font, patch_output)
            if status:
                print("\nTEST: The surgical patch is ready!")
            
            ## SCRIPT TEST
            patch_file = "patch.ttf"
            lite_font_name = "SourceHanSansLite.ttf"
            log_output = "renpatch_log.json"
            generate_renpy_script(success, failed, patch_file, lite_font_name, rpy_output, log_output)
            print("\nPipeline Complete! Drop the generated files into your game folder.")
        else:
            print("No missing characters detected. Your font is healthy!")
            
        
        