/**
 * @file executor.c
 * @brief Implements the command execution logic for the 'run' tool.
 *
 * This file contains the core logic for forking a new process, setting resource
 * limits, executing a command, and collecting performance statistics. It has
 * been refactored to use the central `sniper_log` function for all console output.
 */

#include "executor.h"
#include "utils.h"            // For get_time_diff
#include "sniper_c_utils.h"   // The central utility library for logging

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <sys/resource.h>   // For setrlimit

// Global variable to hold the child process ID for the signal handler.
// This allows the parent to forward signals (like Ctrl+C) to the child.
volatile pid_t g_child_pid = 0;

/**
 * @brief Signal handler that forwards received signals to the running child process.
 * @param signum The signal number received.
 */
void forward_signal_handler(int signum) {
    if (g_child_pid != 0) {
        kill(g_child_pid, signum);
    }
}

/**
 * @brief Executes a command in a new process and captures its results.
 *
 * @param argv The argument vector for the command to execute (must be NULL-terminated).
 * @param verbose If true, prints the command being executed.
 * @param time_limit_sec The maximum CPU time in seconds for the process. 0 for no limit.
 * @param mem_limit_kb The maximum memory (virtual) in kilobytes. 0 for no limit.
 * @return An ExecutionResult struct containing the exit code and performance data.
 */
ExecutionResult execute_command(char *const argv[], bool verbose, long time_limit_sec, long mem_limit_kb) {
    ExecutionResult result = { .exit_code = -1, .real_time_sec = 0.0 };
    memset(&result.usage, 0, sizeof(result.usage));
    struct timespec start, end;

    if (verbose) {
        // Use a temporary buffer to build the full command string for logging
        char command_str[4096] = {0};
        for (int i = 0; argv[i] != NULL; ++i) {
            strncat(command_str, argv[i], sizeof(command_str) - strlen(command_str) - 1);
            strncat(command_str, " ", sizeof(command_str) - strlen(command_str) - 1);
        }
        sniper_log(LOG_DEBUG, "run:exec", "Executing command: %s", command_str);
    }

    clock_gettime(CLOCK_MONOTONIC, &start);

    pid_t pid = fork();
    if (pid == -1) {
        sniper_log(LOG_ERROR, "run:exec", "fork failed: %s", strerror(errno));
        return result;
    }

    if (pid == 0) { // Child process
        // Set resource limits if specified
        if (mem_limit_kb > 0) {
            struct rlimit mem_rlim;
            mem_rlim.rlim_cur = mem_rlim.rlim_max = mem_limit_kb * 1024; // Convert KB to bytes
            if (setrlimit(RLIMIT_AS, &mem_rlim) != 0) {
                // Use sniper_log for warnings within the child process
                sniper_log(LOG_WARN, "run:exec", "Failed to set memory limit: %s", strerror(errno));
            }
        }
        if (time_limit_sec > 0) {
            struct rlimit time_rlim;
            time_rlim.rlim_cur = time_rlim.rlim_max = time_limit_sec;
            if (setrlimit(RLIMIT_CPU, &time_rlim) != 0) {
                sniper_log(LOG_WARN, "run:exec", "Failed to set CPU time limit: %s", strerror(errno));
            }
        }
        
        execvp(argv[0], argv);
        
        // execvp only returns on error
        sniper_log(LOG_ERROR, "run:exec", "Failed to execute '%s': %s", argv[0], strerror(errno));
        exit(127); // Standard exit code for "command not found"

    } else { // Parent process
        g_child_pid = pid;
        int status;
        // wait4 collects resource usage information from the child
        wait4(pid, &status, 0, &result.usage);
        g_child_pid = 0; // Reset global PID

        if (WIFEXITED(status)) {
            result.exit_code = WEXITSTATUS(status);
        } else if (WIFSIGNALED(status)) {
            int term_sig = WTERMSIG(status);
            sniper_log(LOG_WARN, "run:exec", "Process terminated by signal %d (%s)", term_sig, strsignal(term_sig));
            result.exit_code = 128 + term_sig; // Convention for exit by signal
        }
    }
    
    clock_gettime(CLOCK_MONOTONIC, &end);
    result.real_time_sec = get_time_diff(&start, &end);
    return result;
}
