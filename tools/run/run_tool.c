// File: run_tool.c

#include "utils.h"
#include "language.h"
#include "executor.h"
#include "features.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <unistd.h>
#include <libgen.h> // Required for dirname()
#include <signal.h>

// --- NEW Hybrid Help Function ---
void show_rich_help(const char* prog_name) {
    // Check if Python and Rich are available
    if (system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        char command[1024];
        char executable_path[1024];
        char* dir_name;
        
        ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
        if (len != -1) {
            executable_path[len] = '\0';
            dir_name = dirname(executable_path);
            snprintf(command, sizeof(command), "python3 %s/help_printer.py %s", dir_name, prog_name);
            system(command);
        } else {
            // Fallback if readlink fails
            snprintf(command, sizeof(command), "python3 help_printer.py %s", prog_name);
            system(command);
        }
    } else {
        // --- Simple Text Fallback Help ---
        printf("%sUsage: %s [OPTIONS] <file> [file_args...]%s\n", C_BOLD, prog_name, C_RESET);
        printf("A universal code runner for various programming languages.\n");
        printf("%sNOTE:%s For a better help screen, please install Python3 and the 'rich' library (pip install rich).\n\n", C_YELLOW, C_RESET);
        
        printf("%sOPTIONS:%s\n", C_BOLD, C_RESET);
        printf("  %s-h, --help%s           Display this help message and exit.\n", C_GREEN, C_RESET);
        printf("  %s-t, --time%s           Measure and report execution time.\n", C_GREEN, C_RESET);
        printf("  %s-w, --watch%s          Watch the file for changes and re-run.\n\n", C_GREEN, C_RESET);
        printf("%sEXAMPLE:%s\n", C_BOLD, C_RESET);
        printf("  run my_script.py arg1\n");
    }
}


char** build_compiler_argv(const LanguageRecipe* recipe, const char* filepath, const char* temp_executable) {
    int argc_count = 0;
    if (recipe->compiler_args) {
        for (const char** p = recipe->compiler_args; *p; ++p) argc_count++;
    }
    
    // Allocate space for compiler + all args + NULL terminator
    char** argv = malloc(sizeof(char*) * (argc_count + 2));
    if (!argv) return NULL;

    argv[0] = (char*)recipe->compiler;
    int current_arg = 1;
    
    if (recipe->compiler_args) {
        for (const char** p = recipe->compiler_args; *p; ++p) {
            if (strcmp(*p, "$INPUT") == 0) {
                argv[current_arg++] = (char*)filepath;
            } else if (strcmp(*p, "$OUTPUT") == 0) {
                argv[current_arg++] = (char*)temp_executable;
            } else {
                argv[current_arg++] = (char*)*p;
            }
        }
    }
    argv[current_arg] = NULL;
    return argv;
}


int main(int argc, char *argv[]) {
    struct sigaction sa;
    sa.sa_handler = forward_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    bool do_time = false, is_interactive = false;
    bool is_verbose = false, is_watch = false, is_parallel = false;
    long time_limit = 0, mem_limit = 0;

    struct option long_options[] = {
        {"time", no_argument, 0, 't'},
        {"interactive", no_argument, 0, 'i'},
        {"verbose", no_argument, 0, 'v'},
        {"watch", no_argument, 0, 'w'},
        {"parallel", no_argument, 0, 'j'},
        {"no-color", no_argument, 0, 1},
        {"limit-time", required_argument, 0, 2},
        {"limit-mem", required_argument, 0, 3},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "tivwjh", long_options, NULL)) != -1) {
        switch (opt) {
            case 't': do_time = true; break;
            case 'i': is_interactive = true; break;
            case 'v': is_verbose = true; break;
            case 'w': is_watch = true; break;
            case 'j': is_parallel = true; break;
            case 1: g_use_color = false; break;
            case 2: time_limit = atol(optarg); break;
            case 3: mem_limit = atol(optarg); break;
            case 'h':
                show_rich_help(argv[0]); 
                return 0;
            default:
                show_rich_help(argv[0]);
                return 1;
        }
    }
    
    if (optind >= argc && !is_interactive) {
        show_rich_help(argv[0]);
        return 1;
    }

    if (is_interactive) { run_interactive_mode(is_verbose); return 0; }
    if (is_watch) { run_watch_mode(argv[optind], argc, argv, is_verbose); return 0; }
    if (is_parallel) { run_parallel_mode(argc, argv, optind, is_verbose); return 0; }

    const char* filepath = argv[optind];
    const LanguageRecipe* recipe = detect_language(filepath);
    
    if (!recipe) {
        print_error("Unsupported or unrecognized file type for '%s'.", filepath);
        return 1;
    }
    print_info("Detected language: %s", recipe->name);

    char* temp_executable = NULL;
    char** runner_argv = NULL;
    int runner_argc = 0;

    if (recipe->compiler) {
        if (!check_command(recipe->compiler)) {
            print_error("Compiler '%s' not found in PATH.", recipe->compiler);
            return 1;
        }
        
        temp_executable = make_output_name(filepath);
        if (!temp_executable) return 1;

        char** compiler_argv = build_compiler_argv(recipe, filepath, temp_executable);
        if (!compiler_argv) { print_error("Failed to build compiler arguments."); return 1;}

        print_stage("COMPILE", "Compiling with %s...", recipe->compiler);
        
        ExecutionResult compile_res = execute_command(compiler_argv, is_verbose, 0, 0);
        free(compiler_argv);
        if (compile_res.exit_code != 0) {
            print_error("Compilation Failed!");
            return 1;
        }

        runner_argc = (argc - optind); // executable + args...
        runner_argv = malloc((runner_argc + 1) * sizeof(char*));
        if (!runner_argv) { print_error("malloc failed"); return 1; }
        runner_argv[0] = temp_executable;
        // Copy arguments passed to the script itself
        for (int i = 1; i < runner_argc; ++i) {
            runner_argv[i] = argv[optind + i];
        }
        runner_argv[runner_argc] = NULL;
    } else { // Interpreted language
        if (!check_command(recipe->interpreter)) {
            print_error("Interpreter '%s' not found in PATH.", recipe->interpreter);
            return 1;
        }
        
        int prefix_argc = recipe->executor_prefix ? 1 : 0;
        runner_argc = 1 + prefix_argc + (argc - optind); // interpreter + [prefix] + file + file_args...
        runner_argv = malloc((runner_argc + 1) * sizeof(char*));
        if (!runner_argv) { print_error("malloc failed"); return 1; }

        int current_arg = 0;
        runner_argv[current_arg++] = (char*)recipe->interpreter;
        if(recipe->executor_prefix) {
            runner_argv[current_arg++] = (char*)recipe->executor_prefix;
        }
        // Copy the filename and all its arguments
        for (int i = 0; i < (argc - optind); ++i) {
            runner_argv[current_arg++] = argv[optind + i];
        }
        runner_argv[current_arg] = NULL;
    }

    print_stage("EXECUTE", "Running '%s'...", filepath);
    printf("\n");
    ExecutionResult run_res = execute_command(runner_argv, is_verbose, time_limit, mem_limit);

    printf("\n");
    print_stage("REPORT", "Execution finished with exit code %d.", run_res.exit_code);
    if(do_time) {
        print_stage("REPORT", "Real time: %.3fs, User time: %.3fs, Sys time: %.3fs", 
            run_res.real_time_sec, 
            run_res.usage.ru_utime.tv_sec + run_res.usage.ru_utime.tv_usec / 1e6,
            run_res.usage.ru_stime.tv_sec + run_res.usage.ru_stime.tv_usec / 1e6);
        print_stage("REPORT", "Max memory usage: %ld KB", run_res.usage.ru_maxrss);
    }
    
    free(runner_argv);
    // atexit() handles the cleanup of the temp file itself via g_temp_executable_to_cleanup
    
    return run_res.exit_code;
}
