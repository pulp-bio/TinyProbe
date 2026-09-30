

# File tp\_buffer.h

[**File List**](files.md) **>** [**common**](dir_b3d49238ee93ee123788c1fa6c06a286.md) **>** [**tp\_buffer.h**](tp__buffer_8h.md)

[Go to the documentation of this file](tp__buffer_8h.md)


```C++

#pragma once

#include "common.h"

#ifndef TP_BUFFER_HISTORY
#define TP_BUFFER_HISTORY 0
#endif
#ifndef TP_BUFFER_HISTORY_ENTRIES
#define TP_BUFFER_HISTORY_ENTRIES 1024
#endif

typedef enum
{
    TP_BUFFER_FREE,   
    TP_BUFFER_FILLED, 
    TP_BUFFER_INUSE   
} tp_buffer_status_t;

typedef struct
{
    uint8_t data[TP_BUFFER_SIZE]; 
    size_t length;                
    tp_buffer_status_t status;    
    size_t id;                    
} tp_buffer_slot_t;

typedef struct
{
    tp_buffer_slot_t slots[TP_BUFFER_NUM]; 
    size_t head;                           
    size_t tail;                           
    osSemaphoreId_t sem_read;              
    osSemaphoreId_t sem_write;             
} tp_buffer_t;

size_t tp_buffer_history_get(uint32_t **history);

void tp_buffer_history_reset(void);

sl_status_t tp_buffer_init(tp_buffer_t *buf);

tp_buffer_slot_t *tp_buffer_claim_writing(tp_buffer_t *buf);

tp_buffer_slot_t *tp_buffer_claim_reading(tp_buffer_t *buf);

void tp_buffer_return_writing(tp_buffer_t *buf, tp_buffer_slot_t *slot);

void tp_buffer_return_reading(tp_buffer_t *buf, tp_buffer_slot_t *slot);
```


