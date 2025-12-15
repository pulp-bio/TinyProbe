#ifndef SL_IOSTREAM_HANDLES_H
#define SL_IOSTREAM_HANDLES_H
#include "sl_iostream.h"
#include "sl_si91x_iostream_rtt.h"


#ifdef __cplusplus
extern "C" {
#endif

extern const sl_iostream_instance_info_t *sl_iostream_instances_info[];
extern const uint32_t sl_iostream_instances_count;

extern sl_iostream_t *sl_iostream_recommended_console_stream;

sl_iostream_t *sl_iostream_get_handle(const char *name);

void sl_iostream_set_console_instance(void);

#ifdef __cplusplus
}
#endif

#endif // SL_IOSTREAM_HANDLES_H
