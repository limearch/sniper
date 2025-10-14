// File: executor.h | Language: C/C++ Header

#ifndef EXECUTOR_H
#define EXECUTOR_H

#include <stdbool.h>
#include <sys/resource.h>

// Struct to hold the results of an execution
typedef struct {
    int exit_code;
    double real_time_sec;
    struct rusage usage; // For memory and CPU time
} ExecutionResult;

// --- Function Prototypes ---

// Executes a command securely and collects performance data.
ExecutionResult execute_command(char *const argv[], bool verbose, long time_limit_sec, long mem_limit_kb);

// Signal handler to forward signals to the child process.
void forward_signal_handler(int signum); // <<<--- هذا هو السطر المضاف

#endif // EXECUTOR_H
