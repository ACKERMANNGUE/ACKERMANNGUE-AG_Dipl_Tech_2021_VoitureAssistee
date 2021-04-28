// SPDX-License-Identifier: MIT
// Copyright (c) 2018-2020 The Pybricks Authors

#include "py/mpconfig.h"

#if PYBRICKS_PY_IODEVICES && PYBRICKS_PY_PUPDEVICES

#include <pbio/iodev.h>

#include "py/objstr.h"

#include <pybricks/common.h>
#include <pybricks/parameters.h>

#include <pybricks/util_mp/pb_kwarg_helper.h>
#include <pybricks/util_mp/pb_obj_helper.h>
#include <pybricks/util_pb/pb_device.h>
#include <pybricks/util_pb/pb_error.h>

// Class structure for PUPDevice
typedef struct _iodevices_PUPDevice_obj_t {
    mp_obj_base_t base;
    pb_device_t *pbdev;
} iodevices_PUPDevice_obj_t;

// pybricks.iodevices.PUPDevice.__init__
STATIC mp_obj_t iodevices_PUPDevice_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    PB_PARSE_ARGS_CLASS(n_args, n_kw, args,
        PB_ARG_REQUIRED(port));

    iodevices_PUPDevice_obj_t *self = m_new_obj(iodevices_PUPDevice_obj_t);
    self->base.type = (mp_obj_type_t *)type;

    mp_int_t port = pb_type_enum_get_value(port_in, &pb_enum_type_Port);

    self->pbdev = pb_device_get_device(port, PBIO_IODEV_TYPE_ID_LUMP_UART);

    return MP_OBJ_FROM_PTR(self);
}

// pybricks.iodevices.PUPDevice.info
STATIC mp_obj_t iodevices_PUPDevice_info(mp_obj_t self_in) {
    iodevices_PUPDevice_obj_t *self = MP_OBJ_TO_PTR(self_in);

    pbio_port_t _port;
    pbio_iodev_type_id_t id;
    uint8_t curr_mode;
    uint8_t num_values;
    pb_device_get_info(self->pbdev, &_port, &id, &curr_mode, &num_values);

    mp_obj_t info_dict = mp_obj_new_dict(0);
    mp_obj_dict_store(info_dict, MP_ROM_QSTR(MP_QSTR_id), MP_OBJ_NEW_SMALL_INT(id));

    return info_dict;
}
MP_DEFINE_CONST_FUN_OBJ_1(iodevices_PUPDevice_info_obj, iodevices_PUPDevice_info);

// pybricks.iodevices.PUPDevice.read
STATIC mp_obj_t iodevices_PUPDevice_read(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    PB_PARSE_ARGS_METHOD(n_args, pos_args, kw_args,
        iodevices_PUPDevice_obj_t, self,
        PB_ARG_REQUIRED(mode));

    // Get data already in correct data format
    int32_t data[PBIO_IODEV_MAX_DATA_SIZE];
    mp_obj_t objs[PBIO_IODEV_MAX_DATA_SIZE];
    pb_device_get_values(self->pbdev, mp_obj_get_int(mode_in), data);

    // Get info about the sensor and its mode
    pbio_port_t port;
    pbio_iodev_type_id_t id;
    uint8_t curr_mode;
    uint8_t num_values;
    pb_device_get_info(self->pbdev, &port, &id, &curr_mode, &num_values);

    // Return as MicroPython objects
    for (uint8_t i = 0; i < num_values; i++) {
        objs[i] = mp_obj_new_int(data[i]);
    }

    return mp_obj_new_tuple(num_values, objs);
}
MP_DEFINE_CONST_FUN_OBJ_KW(iodevices_PUPDevice_read_obj, 1, iodevices_PUPDevice_read);

// pybricks.iodevices.PUPDevice.write
STATIC mp_obj_t iodevices_PUPDevice_write(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    PB_PARSE_ARGS_METHOD(n_args, pos_args, kw_args,
        iodevices_PUPDevice_obj_t, self,
        PB_ARG_REQUIRED(mode),
        PB_ARG_REQUIRED(data));

    // Unpack the user data tuple
    mp_obj_t *objs;
    size_t num_values;
    mp_obj_get_array(data_in, &num_values, &objs);
    if (num_values > PBIO_IODEV_MAX_DATA_SIZE) {
        pb_assert(PBIO_ERROR_INVALID_ARG);
    }

    // Pack user data to int32_t
    int32_t _data[PBIO_IODEV_MAX_DATA_SIZE];
    for (uint8_t i = 0; i < num_values; i++) {
        _data[i] = mp_obj_get_int(objs[i]);
    }

    // Set the data
    pb_device_set_values(self->pbdev, mp_obj_get_int(mode_in), _data, num_values);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_KW(iodevices_PUPDevice_write_obj, 1, iodevices_PUPDevice_write);

// dir(pybricks.iodevices.PUPDevice)
STATIC const mp_rom_map_elem_t iodevices_PUPDevice_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_read),       MP_ROM_PTR(&iodevices_PUPDevice_read_obj) },
    { MP_ROM_QSTR(MP_QSTR_write),      MP_ROM_PTR(&iodevices_PUPDevice_write_obj)},
    { MP_ROM_QSTR(MP_QSTR_info),       MP_ROM_PTR(&iodevices_PUPDevice_info_obj)},
};
STATIC MP_DEFINE_CONST_DICT(iodevices_PUPDevice_locals_dict, iodevices_PUPDevice_locals_dict_table);

// type(pybricks.iodevices.PUPDevice)
const mp_obj_type_t pb_type_iodevices_PUPDevice = {
    { &mp_type_type },
    .make_new = iodevices_PUPDevice_make_new,
    .locals_dict = (mp_obj_dict_t *)&iodevices_PUPDevice_locals_dict,
};

#endif // PYBRICKS_PY_IODEVICES && PYBRICKS_PY_PUPDEVICES
