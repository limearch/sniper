#ifndef THREADPOOL_H
#define THREADPOOL_H

#include <pthread.h>
#include <stddef.h>

typedef void (*task_function_t)(void *arg);

typedef struct {
    task_function_t function;
    void *argument;
} task_t;

typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t notify;
    pthread_t *threads;
    task_t *queue;
    int thread_count;
    int queue_size;
    int head;
    int tail;
    int count;
    int shutdown;
} threadpool_t;

threadpool_t *threadpool_create(int thread_count, int queue_size);
int threadpool_add(threadpool_t *pool, task_function_t function, void *argument);
int threadpool_destroy(threadpool_t *pool);

#endif // THREADPOOL_H
