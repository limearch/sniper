// File: language.h | Language: C/C++ Header

#ifndef LANGUAGE_H
#define LANGUAGE_H

#include <stdbool.h>

// Defines how to handle a programming language
typedef struct {
    const char* name;
    const char* extension;
    const char* shebang_keyword;
    const char* content_keyword;
    const char* interpreter;
    const char* compiler;
    const char* executor_prefix;
    // Dynamic compiler args. Ends with NULL.
    // Use $INPUT for filepath, $OUTPUT for output executable.
    const char** compiler_args; 
} LanguageRecipe;

// --- Function Prototypes ---

// Finds a recipe that matches the given file path.
// It checks extension, then shebang, then content.
const LanguageRecipe* detect_language(const char* filepath);

#endif // LANGUAGE_H
