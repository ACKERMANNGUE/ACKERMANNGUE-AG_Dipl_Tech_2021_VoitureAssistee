// SPDX-License-Identifier: MIT
// Copyright (c) 2018-2020 The Pybricks Authors

#include "py/mpconfig.h"

#if PYBRICKS_PY_NXTDEVICES && PYBRICKS_PY_EV3DEVICES

#include <pybricks/common.h>
#include <pybricks/nxtdevices.h>
#include <pybricks/parameters.h>

#include <pybricks/util_mp/pb_kwarg_helper.h>
#include <pybricks/util_mp/pb_obj_helper.h>
#include <pybricks/util_pb/pb_device.h>

// pybricks.nxtdevices.TouchSensor class object
typedef struct _nxtdevices_TouchSensor_obj_t {
    mp_obj_base_t base;
    pb_device_t *pbdev;
} nxtdevices_TouchSensor_obj_t;

// pybricks.nxtdevices.TouchSensor.__init__
STATIC mp_obj_t nxtdevices_TouchSensor_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    PB_PARSE_ARGS_CLASS(n_args, n_kw, args,
        PB_ARG_REQUIRED(port));

    nxtdevices_TouchSensor_obj_t *self = m_new_obj(nxtdevices_TouchSensor_obj_t);
    self->base.type = (mp_obj_type_t *)type;

    mp_int_t port = pb_type_enum_get_value(port_in, &pb_enum_type_Port);

    self->pbdev = pb_device_get_device(port, PBIO_IODEV_TYPE_ID_NXT_TOUCH_SENSOR);

    return MP_OBJ_FROM_PTR(self);
}

// pybricks.nxtdevices.TouchSensor.pressed
STATIC mp_obj_t nxtdevices_TouchSensor_pressed(mp_obj_t self_in) {
    nxtdevices_TouchSensor_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int32_t analog;
    pb_device_get_values(self->pbdev, PBIO_IODEV_MODE_EV3_TOUCH_SENSOR__TOUCH, &analog);
    return mp_obj_new_bool(analog < 2500);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(nxtdevices_TouchSensor_pressed_obj, nxtdevices_TouchSensor_pressed);

// dir(pybricks.ev3devices.TouchSensor)
STATIC const mp_rom_map_elem_t nxtdevices_TouchSensor_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_pressed), MP_ROM_PTR(&nxtdevices_TouchSensor_pressed_obj) },
};
STATIC MP_DEFINE_CONST_DICT(nxtdevices_TouchSensor_locals_dict, nxtdevices_TouchSensor_locals_dict_table);

// type(pybricks.ev3devices.TouchSensor)
const mp_obj_type_t pb_type_nxtdevices_TouchSensor = {
    { &mp_type_type },
    .name = MP_QSTR_TouchSensor,
    .make_new = nxtdevices_TouchSensor_make_new,
    .locals_dict = (mp_obj_dict_t *)&nxtdevices_TouchSensor_locals_dict,
};

#endif // PYBRICKS_PY_NXTDEVICES && PYBRICKS_PY_EV3DEVICES
