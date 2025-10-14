/**
 * @file run_tool.c
 * @brief Main entry point and orchestration logic for the 'run' utility.
 *
 * This refactored version leverages the sniper_c_utils library for argument
 * parsing, logging, and help display, resulting in a cleaner and more
 * maintainable codebase.
 */

#include "language.h"
#include "executor.h"
#include "features.h"
#include "utils.h"
#include "sniper_c_utils.h" // The core of the refactoring

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

/**
 * @brief Builds the argument vector (argv) for a compiler command.
 * 
 * Dynamically replaces placeholders like $INPUT and $OUTPUT with actual file paths.
 * 
 * @param recipe The language recipe containing compiler arguments.
 * @param filepath The path to the source file.
 * @param temp_executable The path to the temporary output executable.
 * @return A dynamically allocated argv array, which must be freed by the caller.
 */
static char** build_compiler_argv(const LanguageRecipe* recipe, const char* filepath, const char* temp_executable) {
    int argc_count = 0;
    if (recipe->compiler_args) {
        for (const char** p = recipe->compiler_args; *p; ++p) argc_count++;
    }
    
    // Allocate space for: [compiler, arg1, arg2, ..., NULL]
    char** argv = malloc(sizeof(char*) * (argc_count + 2));
    if (!argv) return NULL;

    argv[0] = (char*)recipe->compiler;
    int current_arg = 1;
    
    if (recipe->compiler_args) {
        for (const char** p = recipe->compiler_args; *p; ++p) {
            if (strcmp(*p, "$INPUT") == 0)      argv[current_arg++] = (char*)filepath;
            else if (strcmp(*p, "$OUTPUT") == 0) argv[current_arg++] = (char*)temp_executable;
            else                                argv[current_arg++] = (char*)*p;
        }
    }
    argv[current_arg] = NULL;
    return argv;
}

int main(int argc, char *argv[]) {
    // --- 1. Setup Signal Handling ---
    // Forward signals like SIGINT (Ctrl+C) to any child process.
    struct sigaction sa;
    sa.sa_handler = forward_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    // --- 2. Define Options for the Parser ---
    bool do_time = false;
    bool is_interactive = false;
    bool is_verbose = false;
    bool is_watch = false;
    bool is_parallel = false;
    int time_limit = 0; // Use int for simplicity with OPT_INT
    int mem_limit = 0;
    
    SniperOption options[] = {
        {'t', "time",         OPT_FLAG,   &do_time,        "Measure execution time."},
        {'i', "interactive",  OPT_FLAG,   &is_interactive, "Enter interactive mode."},
        {'v', "verbose",      OPT_FLAG,   &is_verbose,     "Enable verbose output."},
        {'w', "watch",        OPT_FLAG,   &is_watch,       "Watch file for changes."},
        {'j', "parallel",     OPT_FLAG,   &is_parallel,    "Run files concurrently."},
        {0,   "no-color",     OPT_FLAG,   &g_use_color,    "Disable colored output."},
        {0,   "limit-time",   OPT_INT,    &time_limit,     "Set CPU time limit in seconds."},
        {0,   "limit-mem",    OPT_INT,    &mem_limit,      "Set memory limit in KB."},
        // Terminator for the options array
        {0,   NULL,           (OptionType)0, NULL,         NULL}
    };
    
    // --- 3. Parse Command-Line Arguments ---
    int first_arg_idx = sniper_parse_options(argc, argv, options, "run");

    // The option is --no-color, so if it's true, we set g_use_color to false.
    g_use_color = !g_use_color;
    
    // --- 4. Dispatch to Special Modes ---
    if (is_interactive) {
        run_interactive_mode(is_verbose);
        return 0;
    }

    // Show help if no files are provided for other modes
    if (first_arg_idx >= argc) {
        sniper_show_tool_help("run");
        return 1;
    }

    if (is_watch) {
        run_watch_mode(argv[first_arg_idx], argc, argv, is_verbose);
        return 0; // watch mode is a blocking loop
    }
    if (is_parallel) {
        run_parallel_mode(argc, argv, first_arg_idx, is_verbose);
        return 0;
    }

    // --- 5. Standard Execution Logic ---
    const char* filepath = argv[first_arg_idx];
    const LanguageRecipe* recipe = detect_language(filepath);
    
    if (!recipe) {
        sniper_log(LOG_ERROR, "run", "Unsupported or unrecognized file type for '%s'.", filepath);
        return 1;
    }
    sniper_log(LOG_INFO, "run", "Detected language: %s", recipe->name);

    char* temp_executable = NULL;
    char** runner_argv = NULL;

    if (recipe->compiler) { // --- Compiled Language Logic ---
        if (!check_command(recipe->compiler)) {
            sniper_log(LOG_ERROR, "run", "Compiler '%s' not found in PATH.", recipe->compiler);
            return 1;
        }
        
        temp_executable = make_output_name(filepath);
        if (!temp_executable) return 1;

        char** compiler_argv = build_compiler_argv(recipe, filepath, temp_executable);
        if (!compiler_argv) { sniper_log(LOG_ERROR, "run", "Failed to build compiler arguments."); return 1; }

        sniper_log(LOG_INFO, "run", "Compiling with %s...", recipe->compiler);
        
        ExecutionResult compile_res = execute_command(compiler_argv, is_verbose, 0, 0);
        free(compiler_argv);
        if (compile_res.exit_code != 0) {
            sniper_log(LOG_ERROR, "run", "Compilation Failed!");
            return 1;
        }
        
        int runner_argc = 1 + (argc - first_arg_idx - 1);
        runner_argv = malloc((runner_argc + 1) * sizeof(char*));
        runner_argv[0] = temp_executable;
        for (int i = 1; i < runner_argc; ++i) runner_argv[i] = argv[first_arg_idx + i];
        runner_argv[runner_argc] = NULL;
        
    } else { // --- Interpreted Language Logic ---
        if (!check_command(recipe->interpreter)) {
            sniper_log(LOG_ERROR, "run", "Interpreter '%s' not found in PATH.", recipe->interpreter);
            return 1;
        }
        
        int runner_argc = 1 + (argc - first_arg_idx);
        runner_argv = malloc((runner_argc + 1) * sizeof(char*));
        runner_argv[0] = (char*)recipe->interpreter;
        for (int i = 0; i < (argc - first_arg_idx); ++i) runner_argv[i+1] = argv[first_arg_idx + i];
        runner_argv[runner_argc] = NULL;
    }

    // --- 6. Execute and Report Results ---
    sniper_log(LOG_INFO, "run", "Executing '%s'...", filepath);
    printf("\n"); // Separator for clean program output
    
    ExecutionResult run_res = execute_command(runner_argv, is_verbose, time_limit, mem_limit);

    printf("\n"); // Separator before the final report
    sniper_log(LOG_INFO, "run", "Execution finished with exit code %d.", run_res.exit_code);
    
    if (do_time) {
        double user_time = run_res.usage.ru_utime.tv_sec + run_res.usage.ru_utime.tv_usec / 1e6;
        double sys_time = run_res.usage.ru_stime.tv_sec + run_res.usage.ru_stime.tv_usec / 1e6;
        sniper_log(LOG_INFO, "run", "Real time: %.3fs, User time: %.3fs, Sys time: %.3fs", 
            run_res.real_time_sec, user_time, sys_time);
        sniper_log(LOG_INFO, "run", "Max memory usage: %ld KB", run_res.usage.ru_maxrss);
    }
    
    free(runner_argv);
    // atexit() handler will clean up temp_executable if it was created
    
    return run_res.exit_code;
}
