// SPDX-License-Identifier: MIT
// Copyright (c) 2018-2020 The Pybricks Authors

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include <contiki.h>

#include <pbio/math.h>
#include <pbio/trajectory.h>

static int64_t as_mcount(int32_t count, int32_t count_ext) {
    return ((int64_t)count) * 1000 + count_ext;
}

static void as_count(int64_t mcount, int32_t *count, int32_t *count_ext) {
    *count = (int32_t)(mcount / 1000);
    *count_ext = mcount - ((int64_t)*count) * 1000;
}

void reverse_trajectory(pbio_trajectory_t *ref) {
    // Mirror angles about initial angle th0

    // First load as high res types
    int64_t mth0 = as_mcount(ref->th0, ref->th0_ext);
    int64_t mth1 = as_mcount(ref->th1, ref->th1_ext);
    int64_t mth2 = as_mcount(ref->th2, ref->th2_ext);
    int64_t mth3 = as_mcount(ref->th3, ref->th3_ext);

    // Perform the math
    mth1 = 2 * mth0 - mth1;
    mth2 = 2 * mth0 - mth2;
    mth3 = 2 * mth0 - mth3;

    // Store as simple type again
    as_count(mth1, &ref->th1, &ref->th1_ext);
    as_count(mth2, &ref->th2, &ref->th2_ext);
    as_count(mth3, &ref->th3, &ref->th3_ext);

    // Negate speeds and accelerations
    ref->w0 *= -1;
    ref->w1 *= -1;
    ref->a0 *= -1;
    ref->a2 *= -1;
}

void pbio_trajectory_make_stationary(pbio_trajectory_t *ref, int32_t t0, int32_t th0) {
    // All times equal to initial time:
    ref->t0 = t0;
    ref->t1 = t0;
    ref->t2 = t0;
    ref->t3 = t0;

    // All angles equal to initial angle:
    ref->th0 = th0;
    ref->th1 = th0;
    ref->th2 = th0;
    ref->th3 = th0;

    // FIXME: Angle based does not have high res yet
    ref->th0_ext = 0;
    ref->th1_ext = 0;
    ref->th2_ext = 0;
    ref->th3_ext = 0;

    // All speeds/accelerations zero:
    ref->w0 = 0;
    ref->w1 = 0;
    ref->a0 = 0;
    ref->a2 = 0;

    // This is a finite maneuver
    ref->forever = false;
}

static int64_t x_time(int32_t b, int32_t t) {
    return (((int64_t)b) * ((int64_t)t)) / US_PER_MS;
}

static int64_t x_time2(int32_t b, int32_t t) {
    return x_time(x_time(b, t), t) / (2 * US_PER_MS);
}

pbio_error_t pbio_trajectory_make_time_based(pbio_trajectory_t *ref, int32_t t0, int32_t duration, int32_t th0, int32_t th0_ext, int32_t w0, int32_t wt, int32_t wmax, int32_t a, int32_t amax) {

    // Work with time intervals instead of absolute time. Read 'm' as '-'.
    int32_t t3mt0;
    int32_t t3mt2;
    int32_t t2mt1;
    int32_t t1mt0;

    // Duration of the maneuver
    if (duration == DURATION_FOREVER) {
        // In case of forever, we set the duration to a fictitious 60 seconds.
        t3mt0 = 60 * US_PER_SECOND;
        // This is an infinite maneuver. (This means we'll just ignore the deceleration
        // phase when computing references later, so we keep going even after 60 seconds.)
        ref->forever = true;
    } else {
        // Otherwise, the interval is just the duration
        t3mt0 = duration;
        // This is a finite maneuver
        ref->forever = false;
    }

    // Return error for negative user-specified duration
    if (t3mt0 < 0) {
        return PBIO_ERROR_INVALID_ARG;
    }

    // Remember if the original user-specified maneuver was backward
    bool backward = wt < 0;

    // Convert user parameters into a forward maneuver to simplify computations (we negate results at the end)
    if (backward) {
        wt *= -1;
        w0 *= -1;
    }

    // Limit absolute acceleration
    a = min(a, amax);

    // Limit initial speed
    int32_t max_init = timest(a, t3mt0);
    int32_t abs_max = min(wmax, max_init);
    w0 = max(-abs_max, min(w0, abs_max));
    wt = max(-abs_max, min(wt, abs_max));

    // Initial speed is less than the target speed
    if (w0 < wt) {
        // Therefore accelerate
        ref->a0 = a;
        // If target speed can be reached
        if (wdiva(wt - w0, a) - (t3mt0 - wdiva(w0, a)) / 2 < 0) {
            t1mt0 = wdiva(wt - w0, a);
            ref->w1 = wt;
        }
        // If target speed cannot be reached
        else {
            t1mt0 = (t3mt0 - wdiva(w0, a)) / 2;
            ref->w1 = timest(a, t3mt0) / 2 + w0 / 2;
        }
    }
    // Initial speed is more than the target speed
    else if (w0 > wt) {
        // Therefore decelerate
        ref->a0 = -a;
        t1mt0 = wdiva(w0 - wt, a);
        ref->w1 = wt;
    }
    // Initial speed is equal to the target speed
    else {
        // Therefore no acceleration
        ref->a0 = 0;
        t1mt0 = 0;
        ref->w1 = wt;
    }

    // # Deceleration phase
    ref->a2 = -a;
    t3mt2 = wdiva(ref->w1, a);

    // Constant speed duration
    t2mt1 = t3mt0 - t3mt2 - t1mt0;

    // Assert that all time intervals are positive
    if (t1mt0 < 0 || t2mt1 < 0 || t3mt2 < 0) {
        return PBIO_ERROR_FAILED;
    }

    // Store other results/arguments
    ref->w0 = w0;
    ref->t0 = t0;
    ref->t1 = t0 + t1mt0;
    ref->t2 = t0 + t1mt0 + t2mt1;
    ref->t3 = t0 + t3mt0;

    // Corresponding angle values with millicount/millideg precision
    int64_t mth0 = as_mcount(th0, th0_ext);
    int64_t mth1 = mth0 + x_time(ref->w0, t1mt0) + x_time2(ref->a0, t1mt0);
    int64_t mth2 = mth1 + x_time(ref->w1, t2mt1);
    int64_t mth3 = mth2 + x_time(ref->w1, t3mt2) + x_time2(ref->a2, t3mt2);

    // Store as counts and millicount
    as_count(mth0, &ref->th0, &ref->th0_ext);
    as_count(mth1, &ref->th1, &ref->th1_ext);
    as_count(mth2, &ref->th2, &ref->th2_ext);
    as_count(mth3, &ref->th3, &ref->th3_ext);

    // Reverse the maneuver if the original arguments imposed backward motion
    if (backward) {
        reverse_trajectory(ref);
    }

    return PBIO_SUCCESS;
}

pbio_error_t pbio_trajectory_make_angle_based(pbio_trajectory_t *ref, int32_t t0, int32_t th0, int32_t th3, int32_t w0, int32_t wt, int32_t wmax, int32_t a, int32_t amax) {

    // Return error for zero speed
    if (wt == 0) {
        return PBIO_ERROR_INVALID_ARG;
    }
    // Return error for maneuver that is too long
    if (abs((th3 - th0) / wt) + 1 > DURATION_MAX_S) {
        return PBIO_ERROR_INVALID_ARG;
    }
    // Return empty maneuver for zero angle
    if (th3 == th0) {
        pbio_trajectory_make_stationary(ref, t0, th0);
        return PBIO_SUCCESS;
    }

    // Remember if the original user-specified maneuver was backward
    bool backward = th3 < th0;

    // Convert user parameters into a forward maneuver to simplify computations (we negate results at the end)
    if (backward) {
        th3 = 2 * th0 - th3;
        w0 *= -1;
    }

    // Limit absolute acceleration
    a = min(a, amax);

    // In a forward maneuver, the target speed is always positive.
    wt = abs(wt);
    wt = min(wt, wmax);

    // Limit initial speed
    w0 = max(-wmax, min(w0, wmax));

    // Limit initial speed, but evaluate square root only if necessary (usually not)
    if (w0 > 0 && (w0 * w0) / (2 * a) > th3 - th0) {
        w0 = pbio_math_sqrt(2 * a * (th3 - th0));
    }

    // Initial speed is less than the target speed
    if (w0 < wt) {
        // Therefore accelerate towards intersection from below,
        // either by reaching constant speed phase or not.
        ref->a0 = a;

        // Fictitious zero speed angle (ahead of us if we have negative initial speed; behind us if we have initial positive speed)
        int32_t thf = th0 - (w0 * w0) / (2 * a);

        // Test if we can get to ref speed
        if (th3 - thf >= (wt * wt) / a) {
            //  If so, find both constant speed intersections
            ref->th1 = thf + (wt * wt) / (2 * a);
            ref->th2 = th3 - (wt * wt) / (2 * a);
            ref->w1 = wt;
        } else {
            // Otherwise, intersect halfway between accelerating and decelerating square root arcs
            ref->th1 = (th3 + thf) / 2;
            ref->th2 = ref->th1;
            ref->w1 = pbio_math_sqrt(2 * a * (ref->th1 - thf));
        }
    }
    // Initial speed is equal to or more than the target speed
    else {
        // Therefore decelerate towards intersection from above
        ref->a0 = -a;
        ref->th1 = th0 + (w0 * w0 - wt * wt) / (2 * a);
        ref->th2 = th3 - (wt * wt) / (2 * a);
        ref->w1 = wt;
    }
    // Corresponding time intervals
    int32_t t1mt0 = wdiva(ref->w1 - w0, ref->a0);
    int32_t t2mt1 = ref->th2 == ref->th1 ? 0 : wdiva(ref->th2 - ref->th1, ref->w1);
    int32_t t3mt2 = wdiva(ref->w1, a);

    // Store other results/arguments
    ref->w0 = w0;
    ref->th0 = th0;
    ref->th3 = th3;
    ref->t0 = t0;
    ref->t1 = t0 + t1mt0;
    ref->t2 = ref->t1 + t2mt1;
    ref->t3 = ref->t2 + t3mt2;
    ref->a2 = -a;

    // FIXME: Angle based does not have high res yet
    ref->th0_ext = 0;
    ref->th1_ext = 0;
    ref->th2_ext = 0;
    ref->th3_ext = 0;

    // Reverse the maneuver if the original arguments imposed backward motion
    if (backward) {
        reverse_trajectory(ref);
    }

    // This is a finite maneuver
    ref->forever = false;

    return PBIO_SUCCESS;
}

// Evaluate the reference speed and velocity at the (shifted) time
void pbio_trajectory_get_reference(pbio_trajectory_t *traject, int32_t time_ref, int32_t *count_ref, int32_t *count_ref_ext, int32_t *rate_ref, int32_t *acceleration_ref) {

    int64_t mcount_ref;

    if (time_ref - traject->t1 < 0) {
        // If we are here, then we are still in the acceleration phase. Includes conversion from microseconds to seconds, in two steps to avoid overflows and round off errors
        *rate_ref = traject->w0 + timest(traject->a0, time_ref - traject->t0);
        mcount_ref = as_mcount(traject->th0, traject->th0_ext) + x_time(traject->w0, time_ref - traject->t0) + x_time2(traject->a0, time_ref - traject->t0);
        *acceleration_ref = traject->a0;
    } else if (traject->forever || time_ref - traject->t2 <= 0) {
        // If we are here, then we are in the constant speed phase
        *rate_ref = traject->w1;
        mcount_ref = as_mcount(traject->th1, traject->th1_ext) + x_time(traject->w1, time_ref - traject->t1);
        *acceleration_ref = 0;
    } else if (time_ref - traject->t3 <= 0) {
        // If we are here, then we are in the deceleration phase
        *rate_ref = traject->w1 + timest(traject->a2,    time_ref - traject->t2);
        mcount_ref = as_mcount(traject->th2, traject->th2_ext) + x_time(traject->w1, time_ref - traject->t2) + x_time2(traject->a2, time_ref - traject->t2);
        *acceleration_ref = traject->a2;
    } else {
        // If we are here, we are in the zero speed phase (relevant when holding position)
        *rate_ref = 0;
        mcount_ref = as_mcount(traject->th3, traject->th3_ext);
        *acceleration_ref = 0;
    }

    // Split high res angle into counts and millicounts
    as_count(mcount_ref, count_ref, count_ref_ext);

    // Rebase the reference before it overflows after 35 minutes
    if (time_ref - traject->t0 > (DURATION_MAX_S + 120) * MS_PER_SECOND * US_PER_MS) {
        // Infinite maneuvers just maintain the same reference speed, continuing again from current time
        if (traject->forever) {
            pbio_trajectory_make_time_based(traject, time_ref, DURATION_FOREVER, *count_ref, *count_ref_ext, traject->w1, traject->w1, traject->w1, abs(traject->a2), abs(traject->a2));
        }
        // All other maneuvers are considered complete and just stop. In practice, other maneuvers are not
        // allowed to be this long. This just ensures that if a motor stops and holds, it will continue to
        // do so forever, by rebasing the stationary trajectory before it overflows.
        else {
            pbio_trajectory_make_stationary(traject, time_ref, *count_ref);
        }

    }
}
