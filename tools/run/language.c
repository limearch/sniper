// File: language.c | Language: C

#include "language.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// --- Language Recipes Database ---
// $INPUT and $OUTPUT are placeholders that will be replaced.
const char* C_ARGS[] = {"-o", "$OUTPUT", "$INPUT", "-lm", NULL}; // Common: link math lib
const char* CPP_ARGS[] = {"-std=c++17", "-o", "$OUTPUT", "$INPUT", NULL};
const char* RUST_ARGS[] = {"-o", "$OUTPUT", "$INPUT", NULL};
const char* GO_ARGS[] = {"build", "-o", "$OUTPUT", "$INPUT", NULL};
const char* JAVA_ARGS[] = {"$INPUT", NULL};


LanguageRecipe recipes[] = {
    // Interpreted Languages
    {"Python", ".py", "/usr/bin/python", "import ", "python3", NULL, NULL, NULL},
    {"JavaScript", ".js", "/usr/bin/node", "console.log", "node", NULL, NULL, NULL},
    {"Shell", ".sh", "/bin/bash", "#!/bin/", "bash", NULL, NULL, NULL},
    {"Dart", ".dart", "/usr/bin/dart", "void main()", "dart", NULL, NULL, NULL},
    {"Ruby", ".rb", "/usr/bin/ruby", "puts ", "ruby", NULL, NULL, NULL},
    
    // Compiled Languages
    {"Go", ".go", NULL, "package main", "go", NULL, "run", GO_ARGS}, // Go can also be interpreted with 'go run'
    {"C", ".c", NULL, "#include <stdio.h>", NULL, "gcc", "./", C_ARGS},
    {"C++", ".cpp", NULL, "#include <iostream>", NULL, "g++", "./", CPP_ARGS},
    {"Rust", ".rs", NULL, "fn main()", NULL, "rustc", "./", RUST_ARGS},
    {"Java", ".java", NULL, "public static void main", NULL, "javac", "java", JAVA_ARGS},
    {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL} // Sentinel
};

// --- Language Detection Logic ---
const LanguageRecipe* detect_by_shebang_or_content(const char* filepath) {
    FILE* fp = fopen(filepath, "r");
    if (!fp) return NULL;

    char line[256] = {0};
    if (fgets(line, sizeof(line), fp) == NULL) {
        fclose(fp);
        return NULL;
    }
    fclose(fp); // Close after reading the first line

    // 1. Check Shebang
    if (strncmp(line, "#!", 2) == 0) {
        for (int i = 0; recipes[i].name != NULL; ++i) {
            if (recipes[i].shebang_keyword && strstr(line, recipes[i].shebang_keyword)) {
                return &recipes[i];
            }
        }
    }
    
    // 2. Check Content Keyword
    for (int i = 0; recipes[i].name != NULL; ++i) {
        if (recipes[i].content_keyword && strstr(line, recipes[i].content_keyword)) {
            return &recipes[i];
        }
    }

    return NULL;
}


const LanguageRecipe* detect_language(const char* filepath) {
    const char* file_ext = strrchr(filepath, '.');

    // 1. Detect by extension first (most reliable)
    if (file_ext) {
        for (int i = 0; recipes[i].name != NULL; ++i) {
            if (strcmp(file_ext, recipes[i].extension) == 0) {
                return &recipes[i];
            }
        }
    }

    // 2. If no extension match, try shebang or content
    return detect_by_shebang_or_content(filepath);
}
