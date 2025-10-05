#ifndef CONFIG_H
#define CONFIG_H

// --- بداية التعديل: إضافة 'home' إلى تعريف الدوال ---
int set_value(const char *filepath, const char *home, const char *category, const char *key, const char *value);
int delete_value(const char *filepath, const char *home, const char *category, const char *key);
// --- نهاية التعديل ---

int get_value(const char *filepath, const char *category, const char *key);
void print_help(void);

#endif // CONFIG_H
