// File: tools/secret-hound/src/hound_core/threadpool.hpp
// Description: A simple and efficient thread pool implementation for C.
// Reused from the fastfind tool for consistency and reliability.

#ifndef THREADPOOL_H
#define THREADPOOL_H

#include <pthread.h>
#include <stddef.h>

// Represents a single task to be executed by a worker thread.
typedef void (*task_function_t)(void *arg);

typedef struct {
    task_function_t function;
    void *argument;
} task_t;

// The main thread pool structure.
typedef struct {
    pthread_mutex_t lock;       // Mutex for thread-safe access to the queue
    pthread_cond_t notify;      // Condition variable to signal worker threads
    pthread_t *threads;         // Array of worker threads
    task_t *queue;              // The task queue
    int thread_count;           // Number of threads in the pool
    int queue_size;             // Maximum size of the queue
    int head;                   // Queue head pointer
    int tail;                   // Queue tail pointer
    int count;                  // Current number of tasks in the queue
    int shutdown;               // Flag to signal pool shutdown
} threadpool_t;

/**
 * @brief Creates a new thread pool.
 * @param thread_count The number of worker threads to create.
 * @param queue_size The maximum number of tasks that can be queued.
 * @return A pointer to the newly created threadpool_t, or NULL on failure.
 */
threadpool_t *threadpool_create(int thread_count, int queue_size);

/**
 * @brief Adds a new task to the thread pool's queue.
 * @param pool The thread pool to add the task to.
 * @param function The function pointer for the task to be executed.
 * @param argument The argument to be passed to the task function.
 * @return 0 on success, -1 on failure (e.g., pool is full or shutting down).
 */
int threadpool_add(threadpool_t *pool, task_function_t function, void *argument);

/**
 * @brief Shuts down and destroys the thread pool, freeing all resources.
 * @param pool The thread pool to destroy.
 * @return 0 on success, -1 on failure.
 */
int threadpool_destroy(threadpool_t *pool);

#endif // THREADPOOL_H
