# File: tools/py-shroud/engine/shroud_engine.py (Corrected)
# This script is the entry point for the C wrapper.

import argparse
import sys
import os

# --- CORE FIX: Use explicit relative imports ---
# This tells Python to look for 'core' and 'utils' within the current package ('engine').
try:
    from .core import shroud_file
    from .utils import print_final_report
except ImportError:
    # Fallback for direct execution during development (e.g., python engine/shroud_engine.py)
    # This makes the script more flexible.
    from core import shroud_file
    from utils import print_final_report


def main():
    parser = argparse.ArgumentParser(description="py-shroud obfuscation engine.")
    parser.add_argument('--input', required=True, help="Input Python file.")
    parser.add_argument('--output', required=True, help="Output shrouded file.")
    parser.add_argument('--level', type=int, default=2, help="Obfuscation level.")
    parser.add_argument('--banner', default=None, help="Optional banner file.")
    
    args = parser.parse_args()

    stats = shroud_file(
        input_file=args.input,
        output_file=args.output,
        level=args.level,
        banner_file=args.banner
    )
    
    if stats:
        print_final_report(stats)
        sys.exit(0) # Success
    else:
        # shroud_file already prints the specific error
        sys.exit(1) # Failure

if __name__ == "__main__":
    main()