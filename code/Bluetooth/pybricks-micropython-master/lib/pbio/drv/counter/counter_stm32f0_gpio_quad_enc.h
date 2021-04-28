// SPDX-License-Identifier: MIT
// Copyright (c) 2019-2020 The Pybricks Authors

#ifndef _INTERNAL_PVDRV_COUNTER_STM32F0_GPIO_QUAD_ENC_H_
#define _INTERNAL_PVDRV_COUNTER_STM32F0_GPIO_QUAD_ENC_H_

#include <pbdrv/config.h>

#if PBDRV_CONFIG_COUNTER_STM32F0_GPIO_QUAD_ENC

#include <pbdrv/gpio.h>

#if !PBDRV_CONFIG_COUNTER_STM32F0_GPIO_QUAD_ENC_NUM_DEV
#error Platform must define PBDRV_CONFIG_COUNTER_STM32F0_GPIO_QUAD_ENC_NUM_DEV
#endif

#include <stdbool.h>
#include <stdint.h>

#include <pbdrv/counter.h>
#include <pbdrv/gpio.h>

typedef struct {
    pbdrv_gpio_t gpio_int;
    pbdrv_gpio_t gpio_dir;
    bool invert;
    uint8_t counter_id;
} pbdrv_counter_stm32f0_gpio_quad_enc_platform_data_t;

// defined in platform/*/platform.c
extern const pbdrv_counter_stm32f0_gpio_quad_enc_platform_data_t
    pbdrv_counter_stm32f0_gpio_quad_enc_platform_data[PBDRV_CONFIG_COUNTER_STM32F0_GPIO_QUAD_ENC_NUM_DEV];

void pbdrv_counter_stm32f0_gpio_quad_enc_init(pbdrv_counter_dev_t *devs);

#else // PBDRV_CONFIG_COUNTER_STM32F0_GPIO_QUAD_ENC

#define pbdrv_counter_stm32f0_gpio_quad_enc_init(devs)

#endif // PBDRV_CONFIG_COUNTER_STM32F0_GPIO_QUAD_ENC

#endif // _INTERNAL_PVDRV_COUNTER_STM32F0_GPIO_QUAD_ENC_H_
