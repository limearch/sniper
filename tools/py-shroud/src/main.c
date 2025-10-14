// File: tools/py-shroud/src/main.c (REFACTORED - Complete Code)
// Description: The main C entry point for the py-shroud tool.
// It parses command-line arguments and calls the Python engine.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <libgen.h>
#include <limits.h>

// --- Color Definitions for console output ---
#define C_RED     "\x1B[31m"
#define C_GREEN   "\x1B[32m"
#define C_YELLOW  "\x1B[33m"
#define C_RESET   "\x1B[0m"


// --- START: Centralized Help System Integration ---
/**
 * @brief Prints the help screen for the py-shroud tool.
 *
 * Calls the centralized Python help renderer, falling back to a simple
 * text message if Python/rich is not available.
 *
 * @param prog_name The name of the executable (argv[0]).
 */
void print_help(const char* prog_name) {
    if (system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        // --- Rich Help (Python Call) ---
        char command[PATH_MAX * 2];
        char executable_path[PATH_MAX];

        ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
        if (len != -1) {
            executable_path[len] = '\0';
            
            // Traverse up from .../tools/py-shroud/bin/py-shroud to find the project root
            char* path_copy1 = strdup(executable_path);
            char* p1 = dirname(path_copy1);
            char* path_copy2 = strdup(p1);
            char* p2 = dirname(path_copy2);
            char* path_copy3 = strdup(p2);
            char* p3 = dirname(path_copy3);
            char* project_root = dirname(p3);

            snprintf(command, sizeof(command),
                     "python3 %s/lib/help_renderer.py --tool py-shroud",
                     project_root);
            
            free(path_copy1);
            free(path_copy2);
            free(path_copy3);
            
            system(command);
        } else {
            // Fallback if readlink fails
            system("python3 lib/help_renderer.py --tool py-shroud");
        }
    } else {
        // --- Simple Text Fallback Help ---
        printf("Usage: %s <INPUT_FILE> -o <OUTPUT_FILE> [OPTIONS]\n", prog_name);
        printf("A Python source code obfuscator.\n\n");
        printf("Required:\n");
        printf("  <INPUT_FILE>             The Python source file to shroud.\n");
        printf("  -o, --output <FILE>      Path for the shrouded output file.\n\n");
        printf("Options:\n");
        printf("  -l, --level <1|2|3>      Set obfuscation level (Default: 2).\n");
        printf("  -h, --help               Show this help message.\n");
    }
}
// --- END: Centralized Help System Integration ---


int main(int argc, char *argv[]) {
    // If run with no arguments, show help.
    if (argc == 1) {
        print_help(argv[0]);
        return 0;
    }

    // --- Option Variables ---
    int level = 2; // Default obfuscation level
    const char *output_file = NULL;
    const char *banner_file = NULL;
    const char *input_file = NULL;

    // --- Argument Parsing Setup ---
    struct option long_options[] = {
        {"output", required_argument, 0, 'o'},
        {"level",  required_argument, 0, 'l'},
        {"banner", required_argument, 0, 'b'},
        {"help",   no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "o:l:b:h", long_options, NULL)) != -1) {
        switch (opt) {
            case 'o': output_file = optarg; break;
            case 'l': level = atoi(optarg); break;
            case 'b': banner_file = optarg; break;
            case 'h':
                print_help(argv[0]);
                return 0;
            default:
                return 1;
        }
    }

    // The first non-option argument is the input file.
    if (optind < argc) {
        input_file = argv[optind];
    }

    // --- Input Validation ---
    if (!input_file || !output_file) {
        fprintf(stderr, "%sError: Both an input file and an output file (-o) are required.%s\n\n", C_RED, C_RESET);
        print_help(argv[0]);
        return 1;
    }

    // --- Command Construction & Execution ---
    char tool_root_path[PATH_MAX];
    char executable_path[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
    if (len == -1) {
        fprintf(stderr, "%sError: Could not determine tool path.%s\n", C_RED, C_RESET);
        return 1;
    }
    executable_path[len] = '\0';
    
    // Get the tool's root directory (parent of 'bin/').
    char* path_copy1 = strdup(executable_path);
    char* p1 = dirname(path_copy1);
    char* path_copy2 = strdup(p1);
    char* tool_root = dirname(path_copy2);
    strncpy(tool_root_path, tool_root, PATH_MAX - 1);
    tool_root_path[PATH_MAX - 1] = '\0';
    free(path_copy1);
    free(path_copy2);

    // Convert all user-provided paths to absolute paths to avoid ambiguity.
    char abs_input_path[PATH_MAX];
    char abs_output_path[PATH_MAX];

    if (realpath(input_file, abs_input_path) == NULL) {
        fprintf(stderr, "%sError: Input file '%s' not found.%s\n", C_RED, input_file, C_RESET);
        return 1;
    }
    if (realpath(output_file, abs_output_path) == NULL) {
        // If output file doesn't exist, create its absolute path manually.
        if (output_file[0] != '/') {
            char cwd[PATH_MAX];
            if (getcwd(cwd, sizeof(cwd)) != NULL) {
                snprintf(abs_output_path, sizeof(abs_output_path), "%s/%s", cwd, output_file);
            } else { strncpy(abs_output_path, output_file, PATH_MAX); }
        } else { strncpy(abs_output_path, output_file, PATH_MAX); }
    }

    // Build the command to execute the Python engine.
    char command[PATH_MAX * 4];
    int written = snprintf(command, sizeof(command),
        "sh -c 'cd \"%s\" && python3 -m engine.shroud_engine --input \"%s\" --output \"%s\" --level %d",
        tool_root_path, abs_input_path, abs_output_path, level);

    if (banner_file) {
        char abs_banner_path[PATH_MAX];
        if (realpath(banner_file, abs_banner_path) == NULL) {
            fprintf(stderr, "%sError: Banner file '%s' not found.%s\n", C_RED, banner_file, C_RESET);
            return 1;
        }
        snprintf(command + written, sizeof(command) - written, " --banner \"%s\"'", abs_banner_path);
    } else {
        snprintf(command + written, sizeof(command) - written, "'");
    }
    
    printf("%s[INFO]%s Executing Python obfuscation engine...\n", C_YELLOW, C_RESET);
    int status = system(command);

    if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
        // The Python script prints the final success report.
    } else {
        fprintf(stderr, "\n%s[FAILURE]%s Obfuscation process failed. Check errors above.%s\n", C_RED, C_RED, C_RESET);
        return 1;
    }

    return 0;
}
