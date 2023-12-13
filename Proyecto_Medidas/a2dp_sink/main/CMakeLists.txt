idf_component_register(SRCS "my_queue.c" "volume_control.c" "bt_app_av.c"
                            "bt_app_core.c"
                            "main.c"
                            "../build/config/sdkconfig.h"
                    INCLUDE_DIRS "."
                    INCLUDE_DIRS "../build/esp-idf/freertos"
                    #INCLUDE_DIRS "../build/config"
                    )
                   
#list(APPEND_EXTRA_COMPONENT_DIRS components)

