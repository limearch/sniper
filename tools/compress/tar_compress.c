/**
 * @file tar_compress.c
 * @brief Implements TAR compression by wrapping the system's `tar` command.
 */

#include "tar_compress.h"
#include "sniper_c_utils.h" // For logging

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>

int tar_compress_folder(const char *folder_path, const char *output_file, const char *compression_type, bool verbose) {
    char command[2048];
    const char *comp_flag = "";

    // Determine the correct compression flag for the tar command
    if (compression_type == NULL || strlen(compression_type) == 0) {
        comp_flag = ""; // No compression for plain .tar
    } else if (strcmp(compression_type, "gzip") == 0) {
        comp_flag = "z"; // -z for gzip
    } else if (strcmp(compression_type, "bzip2") == 0) {
        comp_flag = "j"; // -j for bzip2
    } else if (strcmp(compression_type, "xz") == 0) {
        comp_flag = "J"; // -J for xz
    } else {
        sniper_log(LOG_ERROR, "compress:tar", "Unknown compression type '%s'. Use 'gzip', 'bzip2', or 'xz'.", compression_type);
        return 1;
    }

    // Construct the tar command.
    // 'c' - create, 'f' - file.
    // We use '-C' to change to the source directory, ensuring clean relative paths in the archive.
    snprintf(command, sizeof(command), "tar -c%sf %s -C %s .",
             comp_flag, output_file, folder_path);

    if (verbose) {
        sniper_log(LOG_DEBUG, "compress:tar", "Executing command: %s", command);
    }

    // Execute the command via the system's shell
    int result = system(command);

    // Properly check the exit status of the system() call
    if (result == -1) {
        sniper_log(LOG_ERROR, "compress:tar", "system() call failed to execute.");
        return 1;
    } else if (WIFEXITED(result)) {
        if (WEXITSTATUS(result) != 0) {
            sniper_log(LOG_ERROR, "compress:tar", "tar command failed with exit code %d.", WEXITSTATUS(result));
            return 1;
        }
    } else {
        sniper_log(LOG_ERROR, "compress:tar", "tar command did not terminate normally.");
        return 1;
    }

    sniper_log(LOG_SUCCESS, "compress", "Successfully created TAR archive: %s", output_file);
    return 0;
}
