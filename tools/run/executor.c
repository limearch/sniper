// File: executor.c | Language: C

#include "executor.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <time.h>
#include <string.h>
#include <errno.h>
#include <signal.h>

volatile pid_t g_child_pid = 0;

void forward_signal_handler(int signum) {
    if (g_child_pid != 0) {
        kill(g_child_pid, signum);
    }
}

ExecutionResult execute_command(char *const argv[], bool verbose, long time_limit_sec, long mem_limit_kb) {
    ExecutionResult result = { .exit_code = -1, .real_time_sec = 0.0 };
    memset(&result.usage, 0, sizeof(result.usage));
    struct timespec start, end;

    // <<<--- FIX: Use the 'verbose' parameter to provide useful info
    if (verbose) {
        print_info("Executing command:");
        fprintf(stderr, "  ");
        for (int i = 0; argv[i] != NULL; ++i) {
            fprintf(stderr, "%s ", argv[i]);
        }
        fprintf(stderr, "\n");
    }

    clock_gettime(CLOCK_MONOTONIC, &start);

    pid_t pid = fork();
    if (pid == -1) {
        print_error("fork failed: %s", strerror(errno));
        return result;
    }

    if (pid == 0) { // Child process
        // Set resource limits if specified
        if (mem_limit_kb > 0) {
            struct rlimit mem_rlim;
            mem_rlim.rlim_cur = mem_rlim.rlim_max = mem_limit_kb * 1024; // to bytes
            if (setrlimit(RLIMIT_AS, &mem_rlim) != 0) {
                print_warning("Failed to set memory limit: %s", strerror(errno));
            }
        }
        if (time_limit_sec > 0) {
            struct rlimit time_rlim;
            time_rlim.rlim_cur = time_rlim.rlim_max = time_limit_sec;
            if (setrlimit(RLIMIT_CPU, &time_rlim) != 0) {
                print_warning("Failed to set CPU time limit: %s", strerror(errno));
            }
        }
        
        execvp(argv[0], argv);
        // execvp only returns on error
        print_error("Failed to execute '%s': %s", argv[0], strerror(errno));
        exit(127);
    } else { // Parent process
        g_child_pid = pid;
        int status;
        wait4(pid, &status, 0, &result.usage);
        g_child_pid = 0;

        if (WIFEXITED(status)) {
            result.exit_code = WEXITSTATUS(status);
        } else if (WIFSIGNALED(status)) {
            int term_sig = WTERMSIG(status);
            print_warning("Process terminated by signal %d (%s)", term_sig, strsignal(term_sig));
            result.exit_code = 128 + term_sig;
        }
    }
    
    clock_gettime(CLOCK_MONOTONIC, &end);
    result.real_time_sec = get_time_diff(&start, &end);
    return result;
}
