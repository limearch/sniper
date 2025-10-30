#include "regex_utils.h"
#include "search.h"
#include "utils.h"
#include <stdio.h>
#include <string.h>

int compile_regex(Regex *re, const char *pattern, int ignore_case) {
    if (re == NULL || pattern == NULL) return -1;
    re->compiled = 0;
    int cflags = REG_EXTENDED;
    if (ignore_case) cflags |= REG_ICASE;
    int ret = regcomp(&re->regex, pattern, cflags);
    if (ret != 0) {
        char err_buf[256];
        regerror(ret, &re->regex, err_buf, sizeof(err_buf));
        log_error_with_hint("Invalid regex.", err_buf);
        return -1;
    }
    re->compiled = 1;
    return 0;
}

int match_regex(Regex *re, const char *text) {
    if (!re || !re->compiled || !text) return 0;
    return regexec(&re->regex, text, 0, NULL, 0) == 0;
}

void free_regex(Regex *re) {
    if (re && re->compiled) {
        regfree(&re->regex);
        re->compiled = 0;
    }
}

int search_file_content(struct search_config_s *config, const char *path) {
    if (!config->content_regex.compiled || !path) return -1;
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;

    char buffer[4096];
    int match_found = 0;
    int line_num = 1;
    char *line_end;

    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        if (match_regex(&config->content_regex, buffer)) {
            match_found = 1;
            if (config->with_line_number) {
                pthread_mutex_lock(&config->output_lock);
                if ((line_end = strchr(buffer, '\n')) != NULL) *line_end = '\0';
                fprintf(config->out_stream, "%s:%d:%s\n", path, line_num, buffer);
                pthread_mutex_unlock(&config->output_lock);
            } else {
                break;
            }
        }
        line_num++;
    }
    fclose(fp);
    return match_found;
}
