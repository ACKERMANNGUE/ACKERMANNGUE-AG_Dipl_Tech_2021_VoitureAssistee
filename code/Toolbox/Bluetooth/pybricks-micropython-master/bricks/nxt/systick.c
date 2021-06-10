// SPDX-License-Identifier: MIT
// Copyright (c) 2013, 2014 Damien P. George

#include <stdint.h>

#include <pbdrv/config.h>

#include "py/runtime.h"
#include "py/mphal.h"
#include "py/mpconfig.h"

#include <nxt/interrupts.h>
#include <nxt/systick.h>

// Core delay function that does an efficient sleep and may switch thread context.
// If IRQs are enabled then we must have the GIL.
void mp_hal_delay_ms(mp_uint_t Delay) {
    if (interrupts_get()) {
        // IRQs enabled, so can use systick counter to do the delay
        uint32_t start = systick_get_ms();
        // Wraparound of tick is taken care of by 2's complement arithmetic.
        while (systick_get_ms() - start < Delay) {
            // This macro will execute the necessary idle behaviour.  It may
            // raise an exception, switch threads or enter sleep mode (waiting for
            // (at least) the SysTick interrupt).
            MICROPY_EVENT_POLL_HOOK
        }
    } else {
        // IRQs disabled, so need to use a busy loop for the delay.
        systick_wait_ms(Delay);
    }
}
