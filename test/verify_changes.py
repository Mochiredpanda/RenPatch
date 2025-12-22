
import sys
import os
import json

import fontTools

# Add parent directory to path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import generate_renpy_script

def test_generate_renpy_script():
    success_chars = {'A', 'B', 'C'}
    failed_chars = {'X', 'Y', 'Z'}
    patch_filename = "patch.ttf"
    lite_font_filename = "lite.ttf"
    output_path = "test_output.rpy"
    log_path = "test_log.json"

    print("Testing generate_renpy_script...")
    generate_renpy_script(success_chars, failed_chars, patch_filename, lite_font_filename, output_path, log_path)

    # Verify Log
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_data = json.load(f)
        print("Log file exists and contains:")
        print(json.dumps(log_data, indent=2))
        
        assert set(log_data['success']) == {'A', 'B', 'C'}
        assert set(log_data['failed']) == {'X', 'Y', 'Z'}
        print("Log verification PASSED")
    else:
        print("Log verification FAILED: File not found")

    # Verify RPY Script
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            content = f.read()
        
        print("\nGenerated RPY Script content sample:")
        print(content[:500] + "...")
        
        assert "renpatch_font.add('patch.ttf', 0x41, 0x41) # A" in content
        assert "# FAILED: X (U+0058)" in content
        assert "renpatch_font.add('lite.ttf', 0x0000, 0xffff)" in content
        print("\nScript verification PASSED")
    else:
        print("Script verification FAILED: File not found")

    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists(log_path):
        os.remove(log_path)

if __name__ == "__main__":
    test_generate_renpy_script()
