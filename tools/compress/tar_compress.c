// File: tools/compress/tar_compress.c | Language: C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include "tar_compress.h"

int tar_compress_folder(const char *folder_path, const char *output_file, const char *compression_type) {
    // Command buffer: increased size for safety with sh -c wrapper
    char command[2048];
    // Inner command buffer for the tar command itself
    char tar_command[1024];
    const char *comp_flag = "";

    // Determine the correct flag for the tar command
    if (compression_type == NULL || strlen(compression_type) == 0) {
        comp_flag = ""; // No compression flag for plain .tar
    } else if (strcmp(compression_type, "gzip") == 0) {
        comp_flag = "z"; // -z for gzip
    } else if (strcmp(compression_type, "bzip2") == 0) {
        comp_flag = "j"; // -j for bzip2
    } else if (strcmp(compression_type, "xz") == 0) {
        comp_flag = "J"; // -J for xz
    } else {
        fprintf(stderr, "Error: Unknown compression type '%s'. Use 'gzip', 'bzip2', or 'xz'.\n", compression_type);
        return 1;
    }

    // Construct the inner tar command
    // 'c' - create, 'f' - file, plus the optional compression flag 'v' for verbose can be added if needed.
    // We use '-C' to change directory to 'folder_path' before archiving, so paths are relative.
    snprintf(tar_command, sizeof(tar_command), "tar -c%sf %s -C %s .",
             comp_flag, output_file, folder_path);

    // Wrap the command in 'sh -c "..."' for better compatibility, especially in restricted environments like Termux.
    snprintf(command, sizeof(command), "sh -c \"%s\"", tar_command);


    printf("Executing command: %s\n", command);

    // Execute the command via system()
    int result = system(command);

    // The exit code from system() is not the command's exit code directly.
    // We need to check it properly.
    if (result == -1) {
        perror("system() failed");
        return 1;
    } else if (WIFEXITED(result)) {
        if (WEXITSTATUS(result) != 0) {
            fprintf(stderr, "Error: tar command failed with exit code %d.\n", WEXITSTATUS(result));
            return 1;
        }
    } else {
        fprintf(stderr, "Error: tar command did not terminate normally.\n");
        return 1;
    }

    printf("Successfully created TAR archive: %s\n", output_file);
    return 0;
}