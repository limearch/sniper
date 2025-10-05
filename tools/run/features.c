// File: features.c | Language: C

#include "features.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <time.h>
#include <errno.h> // <<<--- FIX: Include for errno and ECHILD

void run_interactive_mode(bool verbose) {
    (void)verbose; // <<<--- FIX: Mark verbose as intentionally unused for now
    print_info("Entering interactive mode. Type 'exit' to quit.");
    char *line = NULL;
    size_t len = 0;

    while (1) {
        printf("%s>> %s", C_BOLD, C_RESET);
        fflush(stdout);
        if (getline(&line, &len, stdin) == -1) break;
        if (line[strlen(line) - 1] == '\n') line[strlen(line) - 1] = '\0';
        if (strcmp(line, "exit") == 0) break;
        if (strlen(line) == 0) continue;
        
        char *const argv[] = {"/bin/sh", "-c", line, NULL};
        
        pid_t pid = fork();
        if (pid == -1) { print_error("fork failed"); continue; }
        if (pid == 0) {
            execv(argv[0], argv);
            print_error("execv failed");
            exit(1);
        }
        wait(NULL);
    }
    free(line);
}

void run_watch_mode(const char* filepath, int argc, char** argv, bool verbose) {
    (void)verbose; // <<<--- FIX: Mark verbose as intentionally unused for now
    print_stage("WATCH", "Watching %s for changes...", filepath);
    time_t last_mtime = get_file_mtime(filepath);
    if (last_mtime == (time_t)-1) {
        print_error("Cannot stat file '%s'", filepath);
        return;
    }

    // Create a new argv for the child without --watch or -w
    char** child_argv = malloc(sizeof(char*) * (argc + 1));
    if (!child_argv) { print_error("malloc failed"); return; }
    int child_argc = 0;
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], "--watch") != 0 && strcmp(argv[i], "-w") != 0) {
            child_argv[child_argc++] = argv[i];
        }
    }
    child_argv[child_argc] = NULL;


    while (1) {
        sleep(1);
        time_t current_mtime = get_file_mtime(filepath);
        if (current_mtime != last_mtime) {
            print_stage("WATCH", "File changed! Rerunning...");
            last_mtime = current_mtime;
            
            pid_t pid = fork();
            if (pid == -1) { print_error("fork failed"); continue; }
            if (pid == 0) {
                execvp(child_argv[0], child_argv);
                print_error("execvp failed");
                exit(1);
            }
            wait(NULL);
            print_stage("WATCH", "Watching %s for changes...", filepath);
        }
    }
    free(child_argv);
}


void run_parallel_mode(int argc, char* argv[], int optind, bool verbose) {
    (void)verbose; // <<<--- FIX: Mark verbose as intentionally unused for now
    int num_files = argc - optind;
    if (num_files <= 0) {
        print_error("No files provided for parallel execution.");
        return;
    }
    pid_t* pids = malloc(num_files * sizeof(pid_t));
    if (!pids) { print_error("malloc failed"); return; }
    
    print_stage("PARALLEL", "Starting %d jobs...", num_files);
    
    // Count original options
    int num_opts = optind;
    
    for (int i = 0; i < num_files; ++i) {
        pids[i] = fork();
        if (pids[i] == -1) { print_error("fork failed for file %s", argv[optind+i]); continue; }
        if (pids[i] == 0) { // Child process
            char* file_to_run = argv[optind + i];
            
            // Reconstruct argv for child process, preserving original options
            char** child_argv = malloc(sizeof(char*) * (num_opts + 2)); // opts + file + NULL
            if (!child_argv) exit(125);
            
            int k = 0;
            // Copy original program name and options
            for (int j = 0; j < num_opts; ++j) {
                // Exclude --parallel/-j flag to avoid recursion
                if(strcmp(argv[j], "--parallel") != 0 && strcmp(argv[j], "-j") != 0) {
                    child_argv[k++] = argv[j];
                }
            }
            child_argv[k++] = file_to_run;
            child_argv[k++] = NULL;

            print_info("[PARALLEL - %s] Starting...", file_to_run);
            execvp(child_argv[0], child_argv);
            print_error("[PARALLEL - %s] execvp failed", file_to_run);
            free(child_argv);
            exit(127);
        }
    }

    // Wait for all children
    int finished_count = 0;
    while(finished_count < num_files) {
        int status;
        pid_t finished_pid = wait(&status);
        if (finished_pid > 0) {
             finished_count++;
             for(int i=0; i < num_files; ++i) {
                 if(pids[i] == finished_pid) {
                     if(WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                         fprintf(stdout, "%s%s[PARALLEL - %s]%s Finished Successfully.%s\n", C_GREEN, C_BOLD, argv[optind+i], C_BOLD, C_RESET);
                     } else {
                         fprintf(stderr, "%s%s[PARALLEL - %s]%s Finished with an Error.%s\n", C_RED, C_BOLD, argv[optind+i], C_BOLD, C_RESET);
                     }
                     break;
                 }
             }
        }
        // <<<--- FIX: Check for errors from wait() correctly
        if (finished_pid == -1 && errno != ECHILD) {
             print_error("wait failed: %s", strerror(errno));
             break;
        }
    }
    
    free(pids);
}
