// File: config.h (Updated)

#ifndef CONFIG_H
#define CONFIG_H

int set_value(const char *filepath, const char *base_path, const char *category, const char *key, const char *value);
int delete_value(const char *filepath, const char *base_path, const char *category, const char *key);
int get_value(const char *filepath, const char *category, const char *key);

// --- CORRECTED PROTOTYPE ---
void print_help(const char *prog_name);

#endif // CONFIG_H
