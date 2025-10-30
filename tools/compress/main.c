/**
 * @file main.c
 * @brief Main entry point for the 'compress' utility.
 *
 * This refactored version leverages the sniper_c_utils library for argument parsing,
 * logging, and help display, which simplifies the main logic and ensures
 * consistency with other C-based tools in the SNIPER toolkit.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Tool-specific headers
#include "zip_tool.h"
#include "tar_compress.h"

// The central SNIPER C utility library
#include "sniper_c_utils.h"

// Main function
int main(int argc, char *argv[]) {
    // --- 1. Define variables and options for the parser ---
    const char *folder_path = NULL;
    const char *output_file = NULL;
    const char *compression_type = NULL; // For TAR
    const char *filter_ext = NULL;
    const char *exclude_ext = NULL;
    bool verbose = false;
    bool test_archive = false;
    bool skip_hidden = false;
    int level = -1; // Default compression level for zip

    // This declarative array defines all command-line options for the tool.
    // It will be processed by the central option parser.
    SniperOption options[] = {
        {'d', "directory",   OPT_STRING, &folder_path,      "Directory to compress."},
        {'o', "output",      OPT_STRING, &output_file,      "Output file name."},
        {'C', "compression", OPT_STRING, &compression_type, "TAR compression type (gzip, bzip2, xz)."},
        {'f', "filter",      OPT_STRING, &filter_ext,       "Only include files with this extension."},
        {'e', "exclude",     OPT_STRING, &exclude_ext,      "Exclude files with this extension."},
        {'l', "level",       OPT_INT,    &level,            "ZIP compression level (0-9)."},
        {'v', "verbose",     OPT_FLAG,   &verbose,          "Enable verbose output."},
        {'t', "test",        OPT_FLAG,   &test_archive,     "Test archive integrity after creation."},
        {'c', "check-integrity", OPT_FLAG, &test_archive,   "Alias for --test."},
        {'H', "skip-hidden", OPT_FLAG,   &skip_hidden,      "Skip hidden files and folders."},
        // The array must be terminated with a NULL/0 entry.
        {0,   NULL,           (OptionType)0, NULL,          NULL}
    };
    
    // --- 2. Parse all command-line options with a single function call ---
    sniper_parse_options(argc, argv, options, "compress");
    
    // --- 3. Validate that required arguments were provided ---
    if (!folder_path || !output_file) {
        // Only show an error if some arguments were provided but were insufficient.
        // If no args are given at all, just show the help screen.
        if (argc > 1) {
            sniper_log(LOG_ERROR, "compress", "Both --directory (-d) and --output (-o) are required.");
        }
        sniper_show_tool_help("compress");
        return 1;
    }
    
    // --- 4. Main Logic: Decide between TAR and ZIP mode ---
    
    // Use TAR mode if the -C flag is used, or if the output filename contains ".tar".
    if (compression_type != NULL || strstr(output_file, ".tar")) {
        const char* final_comp_type = compression_type;
        
        // Auto-detect TAR compression from filename if not explicitly provided.
        if (final_comp_type == NULL) {
            if (strstr(output_file, ".tar.gz") || strstr(output_file, ".tgz")) {
                final_comp_type = "gzip";
            } else if (strstr(output_file, ".tar.bz2") || strstr(output_file, ".tbz2")) {
                final_comp_type = "bzip2";
            } else if (strstr(output_file, ".tar.xz") || strstr(output_file, ".txz")) {
                final_comp_type = "xz";
            }
        }
        
        // Dispatch to the TAR compression function.
        return tar_compress_folder(folder_path, output_file, final_comp_type, verbose);

    } else {
        // Default to ZIP mode for all other cases.
        return compress_folder(
            folder_path, 
            output_file, 
            level, 
            verbose, 
            test_archive, 
            0, // num_threads (not implemented)
            exclude_ext, 
            NULL, // password (not implemented)
            filter_ext, 
            skip_hidden
        );
    }
}
