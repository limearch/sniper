# format_tool/core.py (Corrected and Robust Version)
import os
import shutil
import concurrent.futures


from .formatters.json_formatter import format_json
from .formatters.py_formatter import format_python
from .formatters.generic_formatter import format_c_cpp_java, format_shell
from lib.sniper_env import env
FORMATTERS = {
    '.json': format_json,
    '.py': format_python,
    '.c': format_c_cpp_java,
    '.cpp': format_c_cpp_java,
    '.h': format_c_cpp_java,
    '.sh': format_shell,
}

def process_file(file_path, spaces, backup, verbose, check_mode):
    """
    Processes a single file.
    Returns a tuple: (file_path, needs_formatting_bool)
    """
    _, extension = os.path.splitext(file_path)
    formatter_func = FORMATTERS.get(extension.lower())

    if not formatter_func:
        if verbose:
            env.log.warning(f"Skipping '{os.path.basename(file_path)}': No formatter for '{extension}'")
        return (file_path, False)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        formatted_content = formatter_func(file_path, spaces)

        if formatted_content is None:
            return (file_path, False) # Error in formatter

        # Reliable check for changes
        needs_formatting = (original_content != formatted_content)

        if needs_formatting:
            if check_mode:
                env.log.inf(f"'{file_path}' needs formatting.")
            else:
                if backup:
                    shutil.copy2(file_path, file_path + ".bak")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                
                if verbose:
                    env.log.success(f"Formatted '{file_path}'")
        else:
            if verbose:
                env.log.info(f"'{os.path.basename(file_path)}' is already formatted.")

        return (file_path, needs_formatting)

    except Exception as e:
        env.log.error(f"Failed to process '{file_path}': {e}")
        return (file_path, False)


def format_path(path, spaces, backup, verbose, filter_ext, check_mode, parallel):
    """Main entry point to format a file or a directory."""
    files_to_process = []
    
    if os.path.isfile(path):
        files_to_process.append(path)
    elif os.path.isdir(path):
        if verbose: env.log.info(f"Recursively scanning '{path}'...")
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                if filter_ext:
                    if os.path.splitext(file)[1].lower() in filter_ext:
                        files_to_process.append(full_path)
                else:
                    files_to_process.append(full_path)
    else:
        env.log.error(f"Path '{path}' is not a valid file or directory.")
        return 1

    if not files_to_process:
        env.log.warning("No files found to process.")
        return 0

    files_that_need_formatting = []
    
    tasks = [(f, spaces, backup, verbose, check_mode) for f in files_to_process]

    if parallel and len(files_to_process) > 1:
        if verbose: env.log.info(f"Processing {len(files_to_process)} files in parallel...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(lambda p: process_file(*p), tasks)
            for file_path, needs_formatting in results:
                if needs_formatting:
                    files_that_need_formatting.append(file_path)
    else: # Sequential processing
        for task_args in tasks:
            file_path, needs_formatting = process_file(*task_args)
            if needs_formatting:
                files_that_need_formatting.append(file_path)

    # --- Final Report and Exit Code ---
    if check_mode:
        if files_that_need_formatting:
            env.log.error(f"\nCheck failed: {len(files_that_need_formatting)} file(s) need formatting.")
            return 1 # Exit with error code for CI/CD
        else:
            env.log.info("Check passed: All files are correctly formatted.")
            return 0
    
    env.log.success(f"Formatting complete. {len(files_that_need_formatting)} file(s) were modified.")
    return 0
    