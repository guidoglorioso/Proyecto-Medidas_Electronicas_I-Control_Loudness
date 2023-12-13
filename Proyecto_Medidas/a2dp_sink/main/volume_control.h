#ifndef __VOLUME_CONTROL_H__
#define __VOLUME_CONTROL_H__

#include <stdint.h>
#include "esp_avrc_api.h"
#include <string.h>
#include "freertos/xtensa_api.h"
#include "freertos/FreeRTOSConfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

#include <stdio.h>
#include "my_queue.h"
#include <math.h>
#include "esp_dsp.h"

#define UART_PIN_TXD 1
#define UART_PIN_RXD 3

#define UART_NUM  UART_NUM_0    
#define BUFF_SIZE 300

/* log tags */
#define BT_AV_TAG       "BT_AV"
#define BT_RC_TG_TAG    "RC_TG"
#define BT_RC_CT_TAG    "RC_CT"
#define LOUD_TAG        "LD_DAT"

#define STEREO 1

#ifdef STEREO
#define NUM_CHANNELS 2
#else
#define NUM_CHANNELS 1
#endif

#define FS 44100                // Frecuencia de muestreo
#define WINDOW_TIME 0.4         // Tiempo de cada Ventana
#define SUB_WINDOW_TIME 0.02    // Tiempo de cada SubVentana
#define OFFSET_J 5 //(uint32_t)((WINDOW_TIME*STEP)/SUB_WINDOW_TIME)

#define STEP 0.25

#define SUB_WINDOW_LEN 882 //(uint32_t)(FS * SUB_WINDOW_TIME)                             // Cantidad de muestras por SubVentana
#define CANT_SUB_WINDOWS 20//(uint32_t)(WINDOW_TIME/SUB_WINDOW_TIME)                    // Cantidad de SubVentanas por Ventana
#define NUMBER_OF_WINDOWS 26 //(uint32_t) ((TIME_QUEUE-WINDOW_TIME)/(WINDOW_TIME*STEP)) // Cantidad de Ventanas en Memoria

#define GAMA_A -70 // LKFS


typedef unsigned char uint8_t;
typedef signed char   int8_t ;
typedef float         float32_t;

//the following code changes the volume
uint8_t * volume_control_changeVolume(const uint8_t *data, uint8_t *outputData, size_t size, uint8_t volume);
float32_t abs_float(float32_t num);
uint8_t loudness_algoritmo(float32_t target_loundness,float32_t *correction);
void filter_data(QueueHandle_t queue_datos ,float32_t* data_out);
//void ingresar_datos_medicion(uint8_t *data,size_t size );
void volume_task_handler(void *arg);
void volume_task_start_up();

uint8_t isnumber(const char caracter);
void terminal_task_start_up();
void terminal_task_handler(void *arg);
#endif

