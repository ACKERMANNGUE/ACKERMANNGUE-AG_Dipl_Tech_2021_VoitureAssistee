// SPDX-License-Identifier: MIT
// Copyright (c) 2018-2020 The Pybricks Authors

#include "py/mpconfig.h"

#if PYBRICKS_PY_COMMON

#include "py/obj.h"

#include <pybricks/common.h>

#include <pybricks/util_pb/pb_error.h>
#include <pybricks/util_mp/pb_obj_helper.h>
#include <pybricks/util_mp/pb_kwarg_helper.h>
#include <pybricks/util_mp/pb_obj_helper.h>

// pybricks._common.Light class object
typedef struct _common_LightArray_obj_t {
    mp_obj_base_t base;
    pb_device_t *pbdev;
    uint8_t light_mode;
    uint8_t number_of_lights;
} common_LightArray_obj_t;

// pybricks._common.LightArray.on
STATIC mp_obj_t common_LightArray_on(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    PB_PARSE_ARGS_METHOD(n_args, pos_args, kw_args,
        common_LightArray_obj_t, self,
        PB_ARG_DEFAULT_INT(brightness, 100));

    int32_t brightness_values[4];

    // Given an integer, make all lights the same brightness.
    if (mp_obj_is_int(brightness_in)) {
        int32_t b = pb_obj_get_pct(brightness_in);
        for (uint8_t i = 0; i < self->number_of_lights; i++) {
            brightness_values[i] = b;
        }
    }
    // Otherwise, get each brightness value from list or tuple.
    else {
        mp_obj_t *brightness_objects;
        size_t num_values;
        mp_obj_get_array(brightness_in, &num_values, &brightness_objects);
        if (num_values != self->number_of_lights) {
            pb_assert(PBIO_ERROR_INVALID_ARG);
        }
        for (uint8_t i = 0; i < self->number_of_lights; i++) {
            brightness_values[i] = pb_obj_get_pct(brightness_objects[i]);
        }
    }

    // Set the brightness values
    pb_device_set_values(self->pbdev, self->light_mode, brightness_values, self->number_of_lights);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_KW(common_LightArray_on_obj, 1, common_LightArray_on);

// pybricks._common.LightArray.off
STATIC mp_obj_t common_LightArray_off(mp_obj_t self_in) {
    common_LightArray_obj_t *self = MP_OBJ_TO_PTR(self_in);

    int32_t brightness[4] = {0};
    pb_device_set_values(self->pbdev, self->light_mode, brightness, self->number_of_lights);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(common_LightArray_off_obj, common_LightArray_off);

// dir(pybricks.builtins.LightArray)
STATIC const mp_rom_map_elem_t common_LightArray_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_on), MP_ROM_PTR(&common_LightArray_on_obj) },
    { MP_ROM_QSTR(MP_QSTR_off), MP_ROM_PTR(&common_LightArray_off_obj) },
};
STATIC MP_DEFINE_CONST_DICT(common_LightArray_locals_dict, common_LightArray_locals_dict_table);

// type(pybricks.builtins.LightArray)
STATIC const mp_obj_type_t pb_type_LightArray = {
    { &mp_type_type },
    .name = MP_QSTR_LightArray,
    .locals_dict = (mp_obj_dict_t *)&common_LightArray_locals_dict,
};

// pybricks._common.LightArray.__init__
mp_obj_t common_LightArray_obj_make_new(pb_device_t *pbdev, uint8_t light_mode, uint8_t number_of_lights) {
    // Create new light instance
    common_LightArray_obj_t *light = m_new_obj(common_LightArray_obj_t);
    // Set type and iodev
    light->base.type = &pb_type_LightArray;
    light->pbdev = pbdev;
    light->light_mode = light_mode;
    light->number_of_lights = number_of_lights;
    return light;
}

#endif // PYBRICKS_PY_COMMON
