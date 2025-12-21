import os, sys
import re

from fontTools.ttLib import TTFont
from fontTools import subset

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from core import *

# --- Test Block ---
if __name__ == "__main__":
    # Test with game directory
    test_path = "/Users/jiyuhe/Downloads/game" 
    lite_font = "/Users/jiyuhe/Downloads/game/SourceHanSansLite.ttf"
    full_font = "/Users/jiyuhe/Downloads/game/NotoSansSC.ttf"
    patch_output = "/Users/jiyuhe/Downloads/game/patch.ttf"
    font_name = "SourceHanSansLite.ttf"
    
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
                
        ## TOFU EXTRACTOR TEST
        missing = get_missing_characters(chars, lite_font) 
        print(f"Total missing characters: {len(missing)}")
        print(f"Sample: {''.join(list(missing)[:20])}")
        # Missing Tofu Report
        save_missing_report(missing, "missing_characters.md", font_name)
        
        ## SUBSETTER TEST
        if generate_patch_font(missing, full_font, patch_output):
            print("The surgical patch is ready!")
        