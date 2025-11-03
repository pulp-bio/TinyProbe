#include "sl_main_init.h"
#include "sl_main_kernel.h"

#include "user/user.h"

int main(void)
{
  // Initialize Silicon Labs device, system, service(s) and protocol stack(s).
  sl_main_second_stage_init();

  user_init();
}