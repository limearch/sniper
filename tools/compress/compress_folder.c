/**
 * @file compress_folder.c
 * @brief Main orchestrator for the ZIP compression process.
 */

#include "zip_tool.h"
#include "sniper_c_utils.h" // For logging

#include <stdio.h>
#include <zip.h>
#include <time.h>

int compress_folder(
    const char *folder_path, 
    const char *output_file, 
    int level, 
    bool verbose, 
    bool test_archive, 
    int num_threads, 
    const char *exclude_ext, 
    const char *password, 
    const char *filter_ext, 
    bool skip_hidden
) {
    int errorp;
    // Open the ZIP archive for creation. ZIP_TRUNCATE will overwrite if it exists.
    zip_t *archive = zip_open(output_file, ZIP_CREATE | ZIP_TRUNCATE, &errorp);
    if (!archive) {
        sniper_log(LOG_ERROR, "compress:zip", "Failed to create zip archive: %s", output_file);
        // Note: We cannot use zip_strerror here because the archive is NULL.
        // The error code is in 'errorp'.
        return 1;
    }

    // --- Log configuration notes if verbose mode is on ---
    if (verbose) {
        if (level >= 0) {
            sniper_log(LOG_DEBUG, "compress:zip", "Setting compression level to %d for added files.", level);
        }
        if (password) {
            sniper_log(LOG_WARN, "compress:zip", "Note: Password protection is not implemented in this version.");
        }
        if (num_threads > 1) {
            sniper_log(LOG_WARN, "compress:zip", "Note: Parallel compression is not implemented in this version.");
        }
    }

    // Start timing the operation
    clock_t start = clock();

    // Start the recursive folder compression process
    zip_folder(archive, folder_path, "", verbose, skip_hidden, exclude_ext, filter_ext);

    // Close and save the archive
    if (zip_close(archive) == -1) {
        // Here we can use zip_strerror because the archive object exists.
        sniper_log(LOG_ERROR, "compress:zip", "Error closing zip file: %s", zip_strerror(archive));
        return 1;
    }

    sniper_log(LOG_SUCCESS, "compress", "Successfully created ZIP archive: %s", output_file);

    // Test the archive's integrity if requested
    if (test_archive) {
        if (verbose) {
            sniper_log(LOG_INFO, "compress:zip", "Testing archive integrity...");
        }
        zip_t *test_arc = zip_open(output_file, 0, &errorp);
        if (!test_arc) {
            sniper_log(LOG_ERROR, "compress:zip", "Failed to open archive for testing: %s", output_file);
            return 1;
        }
        zip_close(test_arc);
        sniper_log(LOG_SUCCESS, "compress:zip", "Archive test passed.");
    }

    // Stop timing and print the elapsed time
    clock_t end = clock();
    double elapsed_time = (double)(end - start) / CLOCKS_PER_SEC;
    if (verbose) {
        sniper_log(LOG_INFO, "compress", "Operation completed in %.2f seconds.", elapsed_time);
    }

    return 0;
}
