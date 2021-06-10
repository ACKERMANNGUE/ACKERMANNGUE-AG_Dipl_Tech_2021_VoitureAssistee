// SPDX-License-Identifier: MIT
// Copyright (c) 2018-2020 The Pybricks Authors

#ifndef _PBDRVCONFIG_H_
#define _PBDRVCONFIG_H_

// platform-specific configuration for LEGO MINDSTORMS EV3 running ev3dev-stretch

#define PBDRV_CONFIG_BATTERY                                (1)
#define PBDRV_CONFIG_BATTERY_LINUX_EV3                      (1)

#define PBDRV_CONFIG_BUTTON                                 (1)
#define PBDRV_CONFIG_BUTTON_LINUX_EV3                       (1)

#define PBDRV_CONFIG_CLOCK                                  (1)
#define PBDRV_CONFIG_CLOCK_LINUX                            (1)

#define PBDRV_CONFIG_COUNTER                                (1)
#define PBDRV_CONFIG_COUNTER_NUM_DEV                        (4)
#define PBDRV_CONFIG_COUNTER_EV3DEV_STRETCH_IIO             (1)
#define PBDRV_CONFIG_COUNTER_EV3DEV_STRETCH_IIO_NUM_DEV     (4)

#define PBDRV_CONFIG_COUNTER_COUNTS_PER_DEGREE              (2)

#define PBDRV_CONFIG_IOPORT                                 (1)
#define PBDRV_CONFIG_IOPORT_EV3DEV_STRETCH                  (1)

#define PBDRV_CONFIG_HAS_PORT_A (1)
#define PBDRV_CONFIG_HAS_PORT_B (1)
#define PBDRV_CONFIG_HAS_PORT_C (1)
#define PBDRV_CONFIG_HAS_PORT_D (1)
#define PBDRV_CONFIG_HAS_PORT_1 (1)
#define PBDRV_CONFIG_HAS_PORT_2 (1)
#define PBDRV_CONFIG_HAS_PORT_3 (1)
#define PBDRV_CONFIG_HAS_PORT_4 (1)

#define PBDRV_CONFIG_IOPORT_LPF2_FIRST_PORT PBIO_PORT_1
#define PBDRV_CONFIG_IOPORT_LPF2_LAST_PORT PBIO_PORT_4

#define PBDRV_CONFIG_MOTOR                                  (1)

#define PBDRV_CONFIG_FIRST_MOTOR_PORT PBIO_PORT_A
#define PBDRV_CONFIG_LAST_MOTOR_PORT PBIO_PORT_D
#define PBDRV_CONFIG_NUM_MOTOR_CONTROLLER (4)

#endif // _PBDRVCONFIG_H_
