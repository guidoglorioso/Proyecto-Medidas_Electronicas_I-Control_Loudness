#include <stdio.h>
#include <stdbool.h>

#define TIME_QUEUE  3 //Calculado para un tiempo de 4seg de muestras
#define MAX_QUEUE_SIZE 150 // Time_queue / time_sub_window // Por cada segundo hay 20 muestras

typedef struct {
    float data[MAX_QUEUE_SIZE];
    int front;
    int rear;
} FloatQueue;

void initQueue(FloatQueue *q);

bool isQueueEmpty(FloatQueue *q);

bool isQueueFull(FloatQueue *q);

void enqueue(FloatQueue *q, float item);

float dequeue(FloatQueue *q);

void copyQueueToVector(FloatQueue *q, float *vector);
