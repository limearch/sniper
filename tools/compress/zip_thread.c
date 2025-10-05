// File: tools/compress/zip_thread.c | Language: C

#include <pthread.h>
#include "zip_tool.h"

/**
 * @brief The function that will be executed by each compression thread.
 *
 * This function unpacks the thread_data argument and calls zip_folder
 * with the correct parameters.
 *
 * @param arg A pointer to a thread_data struct.
 * @return NULL.
 */
void* zip_thread(void* arg) {
    thread_data *data = (thread_data*)arg;
    
    // Call the recursive zip_folder function with all the required arguments
    zip_folder(data->archive,
               data->folder_path,
               data->base_path,
               data->verbose,
               data->skip_hidden,
               data->exclude_ext,
               data->filter_ext);
               
    return NULL;
}