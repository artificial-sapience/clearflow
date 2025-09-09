#!/usr/bin/env python3
"""Generate llms-full.txt from llms.txt"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get project root
    project_root = Path(__file__).parent.parent
    llms_txt_path = project_root / "llms.txt"
    llms_full_path = project_root / "llms-full.txt"
    
    # Check if llms.txt exists
    if not llms_txt_path.exists():
        print(f"Error: {llms_txt_path} not found")
        sys.exit(1)
    
    # Generate llms-full.txt using llms_txt2ctx
    try:
        result = subprocess.run(
            ["uv", "run", "llms_txt2ctx", "--optional", "true", str(llms_txt_path)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Write the output to llms-full.txt
        llms_full_path.write_text(result.stdout)
        print(f"Successfully generated {llms_full_path}")
        
        # Display file sizes for verification
        llms_size = llms_txt_path.stat().st_size / 1024
        full_size = llms_full_path.stat().st_size / 1024
        print(f"llms.txt: {llms_size:.1f} KB")
        print(f"llms-full.txt: {full_size:.1f} KB")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating llms-full.txt: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: llms_txt2ctx not found. Install with: uv add --dev llms-txt")
        sys.exit(1)

if __name__ == "__main__":
    main()