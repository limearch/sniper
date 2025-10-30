#ifndef REGEX_UTILS_H
#define REGEX_UTILS_H

#include <regex.h>

struct search_config_s; // Forward declaration

typedef struct {
    regex_t regex;
    int compiled;
} Regex;

int compile_regex(Regex *re, const char *pattern, int ignore_case);
int match_regex(Regex *re, const char *text);
void free_regex(Regex *re);
int search_file_content(struct search_config_s *config, const char *path);

#endif // REGEX_UTILS_H
