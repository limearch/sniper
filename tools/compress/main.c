// File: tools/compress/main.c (Confirmed Correct Version)

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <libgen.h>
#include <unistd.h>
#include "zip_tool.h"
#include "tar_compress.h"

// Hybrid Help Function
void print_help(const char* prog_name) {
    if (system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        char command[1024];
        char executable_path[1024];
        ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
        if (len != -1) {
            executable_path[len] = '\0';
            snprintf(command, sizeof(command), "python3 %s/help_printer.py %s", dirname(executable_path), prog_name);
            system(command);
        } else {
            snprintf(command, sizeof(command), "python3 help_printer.py %s", prog_name);
            system(command);
        }
    } else {
        // Simple Text Fallback Help
        printf("Usage: %s [OPTIONS]\n", prog_name);
        printf("Compress a folder into a ZIP or TAR file.\n");
        printf("(For a better help screen, please install Python3 and the 'rich' library: pip install rich)\n\n");
        
        printf("Options:\n");
        printf("  -d, --directory <path>    Directory to compress (required).\n");
        printf("  -o, --output <file>       Output file name (required).\n");
        printf("  -v, --verbose             Enable verbose mode.\n");
        printf("  -h, --help                Show this help message and exit.\n");
        
        printf("\n--- ZIP Specific Options ---\n");
        printf("  -l, --level <0-9>         Compression level for ZIP.\n");
        printf("  -H, --skip-hidden         Skip hidden files and folders.\n");
        
        printf("\n--- TAR Specific Options ---\n");
        printf("  -C, --compression <type>  Compression type for TAR: gzip, bzip2, or xz.\n\n");
        
        printf("Examples:\n");
        printf("  %s -d my_folder -o my_archive.zip -v\n", prog_name);
        printf("  %s -d my_folder -o my_archive.tar.gz -C gzip\n", prog_name);
    }
}

int main(int argc, char *argv[]) {
    int opt;
    int verbose = 0;
    int skip_hidden = 0;
    int level = -1;
    int test_archive = 0;
    int num_threads = MAX_THREADS;
    const char *exclude_ext = NULL;
    const char *password = NULL;
    const char *filter_ext = NULL;
    const char *compression_type = NULL;

    const char *folder_path = NULL;
    const char *output_file = NULL;

    static struct option long_options[] = {
        {"directory", required_argument, 0, 'd'},
        {"output",    required_argument, 0, 'o'},
        {"level",     required_argument, 0, 'l'},
        {"verbose",   no_argument,       0, 'v'},
        {"test",      no_argument,       0, 't'},
        {"help",      no_argument,       0, 'h'},
        {"skip-hidden", no_argument,     0, 'H'},
        {"parallel",  optional_argument, 0, 'p'},
        {"exclude",   required_argument, 0, 'e'},
        {"password",  required_argument, 0, 'P'},
        {"filter",    required_argument, 0, 'f'},
        {"check-integrity", no_argument, 0, 'c'},
        {"compression", required_argument, 0, 'C'},
        {0, 0, 0, 0}
    };

    while ((opt = getopt_long(argc, argv, "d:o:l:vthHp:e:P:f:cC:", long_options, NULL)) != -1) {
        switch (opt) {
            case 'd': folder_path = optarg; break;
            case 'o': output_file = optarg; break;
            case 'l':
                level = atoi(optarg);
                if (level < 0 || level > 9) {
                    fprintf(stderr, "Invalid compression level: %d. Must be between 0 and 9.\n", level);
                    return 1;
                }
                break;
            case 'v': verbose = 1; break;
            case 't': test_archive = 1; break;
            case 'H': skip_hidden = 1; break;
            case 'p': num_threads = optarg ? atoi(optarg) : MAX_THREADS; break;
            case 'e': exclude_ext = optarg; break;
            case 'P': password = optarg; break;
            case 'f': filter_ext = optarg; break;
            case 'c': test_archive = 1; break;
            case 'C': compression_type = optarg; break;
            case 'h': 
                print_help(argv[0]);
                return 0;
            default:
                fprintf(stderr, "Unknown option. Use -h or --help for usage information.\n");
                return 1;
        }
    }

    if (!folder_path || !output_file) {
        if (argc > 1) {
            fprintf(stderr, "Error: Both --directory and --output must be specified.\n");
        }
        print_help(argv[0]);
        return 1;
    }

    if (compression_type != NULL || strstr(output_file, ".tar")) {
        const char* final_comp_type = compression_type;
        if (final_comp_type == NULL) {
            if (strstr(output_file, ".tar.gz") || strstr(output_file, ".tgz")) final_comp_type = "gzip";
            else if (strstr(output_file, ".tar.bz2") || strstr(output_file, ".tbz2")) final_comp_type = "bzip2";
            else if (strstr(output_file, ".tar.xz") || strstr(output_file, ".txz")) final_comp_type = "xz";
            else {
                 fprintf(stderr, "Warning: Creating an uncompressed TAR file. Use -C <type> for compression.\n");
                 return tar_compress_folder(folder_path, output_file, "");
            }
        }
        return tar_compress_folder(folder_path, output_file, final_comp_type);
    } else {
        return compress_folder(folder_path, output_file, level, verbose, test_archive, num_threads, exclude_ext, password, filter_ext, skip_hidden);
    }
}
