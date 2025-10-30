// File: features.h | Language: C/C++ Header

#ifndef FEATURES_H
#define FEATURES_H

#include <stdbool.h>

// --- Function Prototypes ---
void run_interactive_mode(bool verbose);
void run_watch_mode(const char* filepath, int argc, char** argv, bool verbose);
void run_parallel_mode(int argc, char* argv[], int optind, bool verbose);

#endif // FEATURES_H
