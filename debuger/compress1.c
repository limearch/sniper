#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <zip.h>
#include <dirent.h>
#include <sys/stat.h>
#include <getopt.h>
#include <pthread.h>
#include <time.h>

#define MAX_THREADS 4 // Default to 4 threads

// Function to print help
void print_help() {
    printf("Usage: compress_tool [OPTIONS]\n");
    printf("Compress a folder using ZIP or TAR with chosen compression.\n\n");
    printf("Options:\n");
    printf("  -d, --directory <directory>    Directory to compress.\n");
    printf("  -o, --output <output>          Output file name.\n");
    printf("  -z, --zip                      Use ZIP compression (default).\n");
    printf("  -t, --tar                      Use TAR compression with optional techniques:\n");
    printf("                                 - gzip (default)\n");
    printf("                                 - bzip2\n");
    printf("                                 - xz\n");
    printf("  -c, --compression <technique>  Compression technique for TAR (gzip, bzip2, xz).\n");
    printf("  -v, --verbose                  Enable verbose mode (show files being added).\n");
    printf("  -h, --help                     Show this help message and exit.\n");
}

// Function to compress folder using tar with chosen technique
void compress_tar(const char *folder_path, const char *output_file, const char *compression, int verbose) {
    char command[1024];
    if (strcmp(compression, "gzip") == 0 || strcmp(compression, "") == 0) {
        snprintf(command, sizeof(command), "tar -czf %s.tar.gz -C %s .", output_file, folder_path);
    } else if (strcmp(compression, "bzip2") == 0) {
        snprintf(command, sizeof(command), "tar -cjf %s.tar.bz2 -C %s .", output_file, folder_path);
    } else if (strcmp(compression, "xz") == 0) {
        snprintf(command, sizeof(command), "tar -cJf %s.tar.xz -C %s .", output_file, folder_path);
    } else {
        fprintf(stderr, "Unknown compression technique: %s\n", compression);
        exit(1);
    }

    if (verbose) {
        printf("Executing command: %s\n", command);
    }

    int ret = system(command);
    if (ret == -1) {
        perror("Error executing tar command");
        exit(1);
    }

    if (verbose) {
        printf("Successfully compressed folder %s using TAR with %s compression.\n", folder_path, compression);
    }
}

// Main function
int main(int argc, char *argv[]) {
    int opt;
    int verbose = 0;
    int use_zip = 1; // Default to ZIP
    const char *compression = "gzip"; // Default compression for TAR
    const char *folder_path = NULL;
    const char *output_file = NULL;

    // Define the long options
    static struct option long_options[] = {
        {"directory", required_argument, 0, 'd'},
        {"output", required_argument, 0, 'o'},
        {"zip", no_argument, 0, 'z'},
        {"tar", no_argument, 0, 't'},
        {"compression", required_argument, 0, 'c'},
        {"verbose", no_argument, 0, 'v'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };

    // Parse command-line options
    while ((opt = getopt_long(argc, argv, "d:o:ztc:vh", long_options, NULL)) != -1) {
        switch (opt) {
            case 'd':
                folder_path = optarg;
                break;
            case 'o':
                output_file = optarg;
                break;
            case 'z':
                use_zip = 1;
                break;
            case 't':
                use_zip = 0;
                break;
            case 'c':
                compression = optarg;
                break;
            case 'v':
                verbose = 1;
                break;
            case 'h':
                print_help();
                return 0;
            default:
                fprintf(stderr, "Unknown option. Use -h or --help for usage information.\n");
                return 1;
        }
    }

    if (!folder_path || !output_file) {
        fprintf(stderr, "Both directory and output file must be specified. Use -h or --help for help.\n");
        return 1;
    }

    // Compress using ZIP or TAR
    if (use_zip) {
        printf("ZIP compression is not yet implemented in this version.\n");
        // You can integrate the zip compression logic here
    } else {
        compress_tar(folder_path, output_file, compression, verbose);
    }

    return 0;
}
