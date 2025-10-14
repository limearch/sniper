/**
 * @file features.c
 * @brief Implementation of special modes for the 'run' tool (interactive, watch, parallel).
 *
 * This refactored version uses the central `sniper_log` for all console output,
 * ensuring consistency with the rest of the toolkit.
 */

#include "features.h"
#include "utils.h"          // For get_file_mtime
#include "sniper_c_utils.h" // The central utility library for logging

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <time.h>
#include <errno.h>

/**
 * @brief Starts an interactive REPL-like mode to execute shell commands.
 * @param verbose Unused in this mode, but kept for consistent function signature.
 */
void run_interactive_mode(bool verbose) {
    (void)verbose; // Mark as unused
    sniper_log(LOG_INFO, "run", "Entering interactive mode. Type 'exit' to quit.");
    char *line = NULL;
    size_t len = 0;

    while (1) {
        printf("%s>> %s", C_BOLD, C_RESET); // Custom prompt
        fflush(stdout);
        if (getline(&line, &len, stdin) == -1) break; // End on EOF (Ctrl+D)
        
        // Trim newline character
        line[strcspn(line, "\n")] = 0;

        if (strcmp(line, "exit") == 0) break;
        if (strlen(line) == 0) continue;
        
        // Use /bin/sh to execute the command line
        char *const argv[] = {"/bin/sh", "-c", line, NULL};
        
        pid_t pid = fork();
        if (pid == -1) {
            sniper_log(LOG_ERROR, "run:interactive", "fork failed: %s", strerror(errno));
            continue;
        }
        if (pid == 0) { // Child
            execv(argv[0], argv);
            sniper_log(LOG_ERROR, "run:interactive", "execv failed: %s", strerror(errno));
            exit(127);
        }
        wait(NULL); // Parent waits for child to complete
    }
    free(line);
}

/**
 * @brief Watches a file for changes and re-runs the command upon modification.
 * @param filepath The file to watch.
 * @param argc The original argument count.
 * @param argv The original argument vector.
 * @param verbose Verbosity flag.
 */
void run_watch_mode(const char* filepath, int argc, char** argv, bool verbose) {
    sniper_log(LOG_INFO, "run:watch", "Watching %s for changes...", filepath);
    time_t last_mtime = get_file_mtime(filepath);
    if (last_mtime == (time_t)-1) {
        sniper_log(LOG_ERROR, "run:watch", "Cannot stat file '%s': %s", filepath, strerror(errno));
        return;
    }

    // Create a new argv for the child process, removing the --watch flag to prevent recursion.
    char** child_argv = malloc(sizeof(char*) * (argc + 1));
    if (!child_argv) { sniper_log(LOG_ERROR, "run:watch", "malloc failed"); return; }
    
    int child_argc = 0;
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], "--watch") != 0 && strcmp(argv[i], "-w") != 0) {
            child_argv[child_argc++] = argv[i];
        }
    }
    child_argv[child_argc] = NULL;

    while (1) {
        sleep(1); // Check every second
        time_t current_mtime = get_file_mtime(filepath);
        if (current_mtime > last_mtime) {
            sniper_log(LOG_SUCCESS, "run:watch", "File changed! Rerunning...");
            last_mtime = current_mtime;
            
            pid_t pid = fork();
            if (pid == -1) { sniper_log(LOG_ERROR, "run:watch", "fork failed: %s", strerror(errno)); continue; }
            if (pid == 0) { // Child
                execvp(child_argv[0], child_argv);
                sniper_log(LOG_ERROR, "run:watch", "execvp failed: %s", strerror(errno));
                exit(127);
            }
            wait(NULL); // Parent waits
            sniper_log(LOG_INFO, "run:watch", "Watching %s for changes...", filepath);
        }
    }
    free(child_argv); // This line is technically unreachable but good practice
}

/**
 * @brief Runs multiple files concurrently in parallel processes.
 * @param argc The original argument count.
 * @param argv The original argument vector.
 * @param optind The index of the first file to run.
 * @param verbose Verbosity flag.
 */
void run_parallel_mode(int argc, char* argv[], int optind, bool verbose) {
    int num_files = argc - optind;
    if (num_files <= 0) {
        sniper_log(LOG_ERROR, "run:parallel", "No files provided for parallel execution.");
        return;
    }
    pid_t* pids = malloc(num_files * sizeof(pid_t));
    if (!pids) { sniper_log(LOG_ERROR, "run:parallel", "malloc failed"); return; }
    
    sniper_log(LOG_INFO, "run:parallel", "Starting %d jobs...", num_files);
    
    for (int i = 0; i < num_files; ++i) {
        pids[i] = fork();
        if (pids[i] == -1) {
            sniper_log(LOG_ERROR, "run:parallel", "fork failed for file '%s': %s", argv[optind+i], strerror(errno));
            continue;
        }
        if (pids[i] == 0) { // Child process for one file
            char* file_to_run = argv[optind + i];
            
            // Reconstruct argv for this child, removing the --parallel flag.
            char** child_argv = malloc(sizeof(char*) * (argc + 1));
            if (!child_argv) exit(125);
            
            int k = 0;
            for (int j = 0; j < optind; ++j) {
                if(strcmp(argv[j], "--parallel") != 0 && strcmp(argv[j], "-j") != 0) {
                    child_argv[k++] = argv[j];
                }
            }
            child_argv[k++] = file_to_run;
            child_argv[k++] = NULL; // Terminate the argument list for this single file
            if (verbose) {
                sniper_log(LOG_DEBUG, "run:parallel", "[%s] Starting child process...", file_to_run);
            }
            // Do not log "Starting..." here, as output will be interleaved and messy.
            // The parent process will report success or failure.
            execvp(child_argv[0], child_argv);
            sniper_log(LOG_ERROR, "run:parallel", "[%s] execvp failed: %s", file_to_run, strerror(errno));
            free(child_argv);
            exit(127);
        }
    }

    // Parent process waits for all children to complete.
    int finished_count = 0;
    while(finished_count < num_files) {
        int status;
        pid_t finished_pid = wait(&status);

        if (finished_pid > 0) {
            finished_count++;
            // Find which file corresponds to the finished process
            for(int i=0; i < num_files; ++i) {
                if(pids[i] == finished_pid) {
                    if(WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                        sniper_log(LOG_SUCCESS, "run:parallel", "[%s] Finished successfully.", argv[optind+i]);
                    } else {
                        sniper_log(LOG_ERROR, "run:parallel", "[%s] Finished with an error.", argv[optind+i]);
                    }
                    break;
                }
            }
        } else if (finished_pid == -1 && errno != ECHILD) {
             sniper_log(LOG_ERROR, "run:parallel", "wait failed: %s", strerror(errno));
             break; // Exit loop on wait error
        }
    }
    
    free(pids);
}
