from lib.sniper_env import env
def format_with_external_tool(file_path, command_args, command_name):
    """Generic function to format using an external tool by reading stdout."""
    if not env.command_exists(command_name):
        env.log.warning(f"Command '{command_name}' not found. Skipping {file_path}.")
        return None
    
    try:
        # Run the command and capture its stdout
        full_command = command_args + [file_path]
        result = env.run_command(full_command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        env.log.error(f"Error formatting {file_path} with {command_name}: {e.stderr}")
        return None

def format_c_cpp_java(file_path, spaces=4):
    return format_with_external_tool(file_path, ['clang-format', f'-style={{IndentWidth: {spaces}}}'], 'clang-format')

def format_shell(file_path, spaces=4):
    return format_with_external_tool(file_path, ['shfmt', '-i', str(spaces)], 'shfmt')
    