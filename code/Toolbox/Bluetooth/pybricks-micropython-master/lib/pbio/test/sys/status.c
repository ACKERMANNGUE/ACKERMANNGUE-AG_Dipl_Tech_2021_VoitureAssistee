// SPDX-License-Identifier: MIT
// Copyright (c) 2020-2021 The Pybricks Authors

#include <stdbool.h>
#include <stdio.h>

#include <contiki.h>
#include <tinytest.h>
#include <tinytest_macros.h>

#include <pbio/event.h>
#include <pbsys/status.h>
#include <test-pbio.h>

PROCESS(status_test_process, "status test");

static process_event_t last_event;
static process_data_t last_data;

PROCESS_THREAD(status_test_process, ev, data) {
    PROCESS_BEGIN();

    for (;;) {
        PROCESS_WAIT_EVENT();
        last_event = ev;
        last_data = data;
    }

    PROCESS_END();
}

static PT_THREAD(test_status(struct pt *pt)) {
    PT_BEGIN(pt);

    process_start(&status_test_process, NULL);

    // use the last valid flag for edge case
    static const pbio_pybricks_status_t test_flag = NUM_PBIO_PYBRICKS_STATUS - 1;

    // ensure flags are initalized as unset
    tt_want(!pbsys_status_test(test_flag));

    // ensure that setting a flag works as expected
    pbsys_status_set(test_flag);
    tt_want(pbsys_status_test(test_flag));
    tt_want(!pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(!pbsys_status_test_debounce(test_flag, false, 10));

    // ensure that event was broadcast
    last_event = PROCESS_EVENT_NONE;
    PT_YIELD(pt);
    tt_want_uint_op(last_event, ==, PBIO_EVENT_STATUS_SET);
    tt_want_uint_op(last_data, ==, test_flag);

    // ensure that debounce works
    clock_tick(clock_from_msec(9));
    PT_YIELD(pt);
    tt_want(!pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(!pbsys_status_test_debounce(test_flag, false, 10));
    clock_tick(clock_from_msec(1));
    PT_YIELD(pt);
    tt_want(pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(!pbsys_status_test_debounce(test_flag, false, 10));

    // ensure that setting a flag again does not reset debounce timer or broadcast event
    pbsys_status_set(test_flag);
    tt_want(pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(!pbsys_status_test_debounce(test_flag, false, 10));

    last_event = PROCESS_EVENT_NONE;
    PT_YIELD(pt);
    tt_want_uint_op(last_event, ==, PROCESS_EVENT_NONE);

    // ensure that clearing a flag works as expected
    pbsys_status_clear(test_flag);
    tt_want(!pbsys_status_test(test_flag));
    tt_want(!pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(!pbsys_status_test_debounce(test_flag, false, 10));

    // ensure that event was broadcast
    last_event = PROCESS_EVENT_NONE;
    PT_YIELD(pt);
    tt_want_uint_op(last_event, ==, PBIO_EVENT_STATUS_CLEARED);
    tt_want_uint_op(last_data, ==, test_flag);

    // ensure that debounce works
    last_event = PROCESS_EVENT_NONE;
    clock_tick(clock_from_msec(9));
    PT_YIELD(pt);
    tt_want(!pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(!pbsys_status_test_debounce(test_flag, false, 10));
    clock_tick(clock_from_msec(1));
    PT_YIELD(pt);
    tt_want(!pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(pbsys_status_test_debounce(test_flag, false, 10));

    // ensure that clearing a flag again does not reset debounce timer or broadcast
    pbsys_status_clear(test_flag);
    tt_want(!pbsys_status_test_debounce(test_flag, true, 10));
    tt_want(pbsys_status_test_debounce(test_flag, false, 10));

    last_event = PROCESS_EVENT_NONE;
    PT_YIELD(pt);
    tt_want_uint_op(last_event, ==, PROCESS_EVENT_NONE);

    PT_END(pt);
}

struct testcase_t pbsys_status_tests[] = {
    PBIO_PT_THREAD_TEST(test_status),
    END_OF_TESTCASES
};
