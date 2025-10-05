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
#include <signal.h>

static void show_rich_help(const char* prog_name) {
    int width = get_terminal_width();

    char title_buffer[256];
    snprintf(title_buffer, sizeof(title_buffer), "%sSNIPER: run - Universal Code Runner%s", C_BOLD, C_RESET);
    print_panel_top("", C_MAGENTA, width);
    print_panel_line(title_buffer, C_MAGENTA, width);
    print_panel_separator(C_MAGENTA, width);
    print_panel_line("A powerful tool to compile, run, and manage code for various languages.", C_MAGENTA, width);
    print_panel_bottom(C_MAGENTA, width);

    char usage_buffer[256];
    snprintf(usage_buffer, sizeof(usage_buffer), "  %sUsage:%s %s%s%s %s<file>%s %s[args...]%s",
           C_BOLD, C_RESET, C_YELLOW, prog_name, C_RESET, C_CYAN, C_RESET, C_GREEN, C_RESET);
    printf("\n%s\n\n", usage_buffer);
    
    print_panel_top("Options", C_BLUE, width);
    print_panel_line("  -t, --time           Measure execution time and memory usage.", C_BLUE, width);
    print_panel_line("  -v, --verbose        Enable verbose output for compilation/execution.", C_BLUE, width);
    print_panel_line("  -w, --watch          Watch the file for changes and re-run automatically.", C_BLUE, width);
    print_panel_line("  -j, --parallel       Run multiple files in parallel.", C_BLUE, width);
    print_panel_line("  -i, --interactive    Run in interactive shell mode.", C_BLUE, width);
    print_panel_line("      --limit-time N   Set CPU time limit of N seconds.", C_BLUE, width);
    print_panel_line("      --limit-mem N    Set memory limit of N kilobytes.", C_BLUE, width);
    print_panel_line("      --no-color       Disable all colored output.", C_BLUE, width);
    print_panel_line("  -h, --help           Display this help message.", C_BLUE, width);
    print_panel_bottom(C_BLUE, width);

    print_panel_top("Examples", C_GREEN, width);
    print_panel_line("  # Run a Python script with arguments", C_GREEN, width);
    print_panel_line("  run my_script.py arg1 \"hello world\"", C_GREEN, width);
    print_panel_line(" ", C_GREEN, width);
    print_panel_line("  # Compile and run a C program with performance report", C_GREEN, width);
    print_panel_line("  run --time --limit-mem 16384 my_program.c", C_GREEN, width);
    print_panel_line(" ", C_GREEN, width);
    print_panel_line("  # Automatically re-run a server on file changes", C_GREEN, width);
    print_panel_line("  run --watch server.js", C_GREEN, width);
    print_panel_bottom(C_GREEN, width);
    
    print_panel_top("Dependencies", C_YELLOW, width);
    print_panel_line("  - For compiled languages, a compiler must be in your PATH.", C_YELLOW, width);
    print_panel_line("    (e.g., 'gcc' for C, 'g++' for C++, 'rustc' for Rust, etc.)", C_YELLOW, width);
    print_panel_line("  - For interpreted languages, an interpreter must be in your PATH.", C_YELLOW, width);
    print_panel_line("    (e.g., 'python3', 'node', 'ruby', etc.)", C_YELLOW, width);
    print_panel_bottom(C_YELLOW, width);
}


char** build_compiler_argv(const LanguageRecipe* recipe, const char* filepath, const char* temp_executable) {
    int argc_count = 0;
    if (recipe->compiler_args) {
        for (const char** p = recipe->compiler_args; *p; ++p) argc_count++;
    }
    
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
            default: return 1;
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

        runner_argc = argc - optind;
        runner_argv = malloc((runner_argc + 1) * sizeof(char*));
        if (!runner_argv) { print_error("malloc failed"); return 1; }
        runner_argv[0] = temp_executable;
        for (int i = 1; i < runner_argc; ++i) runner_argv[i] = argv[optind + i];
        runner_argv[runner_argc] = NULL;
    } else {
        if (!check_command(recipe->interpreter)) {
            print_error("Interpreter '%s' not found in PATH.", recipe->interpreter);
            return 1;
        }
        
        runner_argc = (argc - optind) + (recipe->executor_prefix ? 2 : 1);
        runner_argv = malloc((runner_argc + 1) * sizeof(char*));
        if (!runner_argv) { print_error("malloc failed"); return 1; }

        int current_arg = 0;
        runner_argv[current_arg++] = (char*)recipe->interpreter;
        if(recipe->executor_prefix) {
            runner_argv[current_arg++] = (char*)recipe->executor_prefix;
        }
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
    // atexit handles cleanup
    
    return run_res.exit_code;
}
