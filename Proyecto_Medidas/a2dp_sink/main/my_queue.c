
#include "my_queue.h"


void initQueue(FloatQueue *q) {
    q->front = -1;
    q->rear = -1;
}

bool isQueueEmpty(FloatQueue *q) {
    return (q->front == -1);
}

bool isQueueFull(FloatQueue *q) {
    if (q->front == -1) {
        // La cola está vacía
        return false;
    }

    int nextRear = (q->rear + 1) % MAX_QUEUE_SIZE;
    return (nextRear == q->front);
}


void enqueue(FloatQueue *q, float item) {
    if (isQueueFull(q)) {
        // La cola está llena, pisa el primer dato y mueve el frente
        q->front = (q->front + 1) % MAX_QUEUE_SIZE;
    }

    if (isQueueEmpty(q)) {
        q->front = 0;
    }
    //printf("Actual Rear= %i; item to add= %f\n",q->rear,item);
    q->rear = (q->rear + 1) % MAX_QUEUE_SIZE;
    //printf("Rear: %i\n",q->rear);
    q->data[q->rear] = item;
}


float dequeue(FloatQueue *q) {
    float item = 0.0;  // Valor por defecto
    if (isQueueEmpty(q)) {
        printf("Queue is empty. Cannot dequeue.\n");
    } else {
        item = q->data[q->front];
        if (q->front == q->rear) {
            q->front = q->rear = -1;
        } else {
            q->front = (q->front + 1) % MAX_QUEUE_SIZE;
        }
    }
    return item;
}

// Función para copiar los elementos de la cola a un vector
void copyQueueToVector(FloatQueue *q, float *vector) {
    int i = q->front;
    int count = 0;

    if (isQueueEmpty(q)) {
        return;  // La cola está vacía
    }

    do {
        vector[count] = q->data[i];
        count += 1;
        i = (i + 1) % MAX_QUEUE_SIZE;
    } while (i != (q->rear + 1) % MAX_QUEUE_SIZE);
}


