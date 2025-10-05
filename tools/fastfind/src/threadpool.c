#include "threadpool.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

static void *threadpool_worker(void *arg) {
    threadpool_t *pool = (threadpool_t *)arg;
    task_t task;

    while (1) {
        pthread_mutex_lock(&(pool->lock));

        while (pool->count == 0 && !pool->shutdown) {
            pthread_cond_wait(&(pool->notify), &(pool->lock));
        }

        if (pool->shutdown && pool->count == 0) {
            break;
        }

        task.function = pool->queue[pool->head].function;
        task.argument = pool->queue[pool->head].argument;
        pool->head = (pool->head + 1) % pool->queue_size;
        pool->count--;

        pthread_mutex_unlock(&(pool->lock));
        (*(task.function))(task.argument);
    }

    pthread_mutex_unlock(&(pool->lock));
    pthread_exit(NULL);
    return NULL;
}

threadpool_t *threadpool_create(int thread_count, int queue_size) {
    if (thread_count <= 0 || queue_size <= 0) return NULL;

    threadpool_t *pool = (threadpool_t *)malloc(sizeof(threadpool_t));
    if (pool == NULL) return NULL;

    pool->thread_count = 0;
    pool->queue_size = queue_size;
    pool->head = pool->tail = pool->count = 0;
    pool->shutdown = 0;

    pool->threads = (pthread_t *)malloc(sizeof(pthread_t) * thread_count);
    pool->queue = (task_t *)malloc(sizeof(task_t) * queue_size);

    if (pthread_mutex_init(&(pool->lock), NULL) != 0 ||
        pthread_cond_init(&(pool->notify), NULL) != 0 ||
        pool->threads == NULL || pool->queue == NULL) {
        if (pool->threads) free(pool->threads);
        if (pool->queue) free(pool->queue);
        free(pool);
        return NULL;
    }

    for (int i = 0; i < thread_count; i++) {
        if (pthread_create(&(pool->threads[i]), NULL, threadpool_worker, (void *)pool) != 0) {
            threadpool_destroy(pool);
            return NULL;
        }
        pool->thread_count++;
    }
    return pool;
}

int threadpool_add(threadpool_t *pool, task_function_t function, void *argument) {
    if (pool == NULL || function == NULL) return -1;
    pthread_mutex_lock(&(pool->lock));
    if (pool->count == pool->queue_size || pool->shutdown) {
        pthread_mutex_unlock(&(pool->lock));
        return -1;
    }

    pool->queue[pool->tail].function = function;
    pool->queue[pool->tail].argument = argument;
    pool->tail = (pool->tail + 1) % pool->queue_size;
    pool->count++;

    pthread_cond_signal(&(pool->notify));
    pthread_mutex_unlock(&(pool->lock));
    return 0;
}

int threadpool_destroy(threadpool_t *pool) {
    if (pool == NULL) return -1;
    pthread_mutex_lock(&(pool->lock));
    if (pool->shutdown) {
        pthread_mutex_unlock(&(pool->lock));
        return -1;
    }
    pool->shutdown = 1;
    pthread_cond_broadcast(&(pool->notify));
    pthread_mutex_unlock(&(pool->lock));
    for (int i = 0; i < pool->thread_count; i++) {
        pthread_join(pool->threads[i], NULL);
    }
    free(pool->threads);
    free(pool->queue);
    pthread_mutex_destroy(&(pool->lock));
    pthread_cond_destroy(&(pool->notify));
    free(pool);
    return 0;
}
