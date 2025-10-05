#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"

// أضفنا تعريفات الألوان هنا للوصول السريع
#define KGRN "\x1B[32m"
#define KWHT "\x1B[37m"
#define KRESET "\x1B[0m"

int main(int argc, char *argv[]) {
    const char *home = getenv("HOME");
    if (!home) {
        fprintf(stderr, "HOME environment variable not found.\n");
        return 1;
    }

    char filepath[512];
    snprintf(filepath, sizeof(filepath), "%s/.config/sniper-config.json", home);

    if (argc < 2) {
        print_help();
        return 1;
    }

    if (strcmp(argv[1], "help") == 0) {
        print_help();
        return 0;
    }

    // --- بداية التعديلات ---

    if (strcmp(argv[1], "set") == 0 && argc == 5) {
        // تم تمرير متغير 'home' لإنشاء سجل التغييرات (log)
        int result = set_value(filepath, home, argv[2], argv[3], argv[4]);
        if (result == 0) {
            printf(KGRN "✔ Success:" KWHT " Value was set successfully.\n" KRESET);
        }
        return result;
    } else if (strcmp(argv[1], "get") == 0 && argc == 4) {
        // دالة get تطبع القيمة بنفسها عند النجاح، لذا لا تحتاج رسالة إضافية
        return get_value(filepath, argv[2], argv[3]);
    } else if (strcmp(argv[1], "delete") == 0 && argc == 4) {
        // تم تمرير متغير 'home' لإنشاء سجل التغييرات (log)
        int result = delete_value(filepath, home, argv[2], argv[3]);
        if (result == 0) {
            printf(KGRN "✔ Success:" KWHT " Value was deleted successfully.\n" KRESET);
        }
        return result;
    } else {
        print_help();
        return 1;
    }
    // --- نهاية التعديلات ---
}
