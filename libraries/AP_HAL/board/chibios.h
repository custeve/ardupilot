#pragma once

#define HAL_BOARD_NAME "ChibiOS"
#define HAL_CPU_CLASS HAL_CPU_CLASS_150
#define HAL_STORAGE_SIZE            16384
#define HAL_STORAGE_SIZE_AVAILABLE  HAL_STORAGE_SIZE
#define HAL_INS_DEFAULT HAL_INS_LSM9DS0
#define HAL_BARO_DEFAULT HAL_BARO_HIL
#define CONFIG_HAL_BOARD_SUBTYPE HAL_BOARD_SUBTYPE_CHIBIOS_NUCLEO_F412

#define HAL_GPIO_A_LED_PIN        0
#define HAL_GPIO_B_LED_PIN        1
#define HAL_GPIO_C_LED_PIN        2
#define HAL_GPIO_LED_ON           LOW
#define HAL_GPIO_LED_OFF          HIGH

#define HAL_HAVE_BOARD_VOLTAGE 0
#define HAL_HAVE_SAFETY_SWITCH 0

#define HAL_INS_MPU9250_NAME "mpu9250"
#define HAL_BARO_BMP280_NAME	"bmp280"

#define HAL_INS_LSM9DS0_G_NAME "lsm303d"
#define HAL_INS_LSM9DS0_A_NAME "l3gd20h"