// File: config.h (Updated)

#ifndef CONFIG_H
#define CONFIG_H

// --- تم التعديل: استبدال 'home' بـ 'base_path' لمرونة أكبر ---
int set_value(const char *filepath, const char *base_path, const char *category, const char *key, const char *value);
int delete_value(const char *filepath, const char *base_path, const char *category, const char *key);
// --- نهاية التعديل ---

int get_value(const char *filepath, const char *category, const char *key);
void print_help(void);

#endif // CONFIG_H
