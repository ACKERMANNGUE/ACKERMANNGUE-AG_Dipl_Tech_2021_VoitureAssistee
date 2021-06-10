// SPDX-License-Identifier: MIT
// Copyright (c) 2019-2020 The Pybricks Authors

// ev3dev-stretch I/O port

#ifndef _INTERNAL_PBDRV_IOPORT_EV3DEV_STRETCH_H_
#define _INTERNAL_PBDRV_IOPORT_EV3DEV_STRETCH_H_

#include <pbio/error.h>
#include <pbio/port.h>

pbio_error_t pbdrv_ioport_ev3dev_get_syspath(pbio_port_t port, const char **syspath);

#endif // _INTERNAL_PBDRV_IOPORT_EV3DEV_STRETCH_H_
