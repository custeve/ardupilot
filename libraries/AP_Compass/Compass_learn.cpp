#include <AP_Math/AP_Math.h>
#include <AP_AHRS/AP_AHRS.h>

#include <AP_Compass/AP_Compass.h>
#include <AP_Declination/AP_Declination.h>
#include <DataFlash/DataFlash.h>

#include "Compass_learn.h"

#include <stdio.h>

extern const AP_HAL::HAL &hal;

// constructor
CompassLearn::CompassLearn(AP_AHRS &_ahrs, Compass &_compass) :
    ahrs(_ahrs),
    compass(_compass)
{
}

/*
  update when new compass sample available
 */
void CompassLearn::update(void)
{
    if (!hal.util->get_soft_armed() || ahrs.get_time_flying_ms() < 3000) {
        // only learn when flying and with enough time to be clear of
        // the ground
        return;
    }

    if (!have_earth_field) {
        Location loc;
        if (!ahrs.get_position(loc)) {
            // need to wait till we have a global position
            return;
        }

        // setup the expected earth field at this location
        float declination_deg=0, inclination_deg=0, intensity_gauss=0;
        AP_Declination::get_mag_field_ef(loc.lat*1.0e-7, loc.lng*1.0e-7, intensity_gauss, declination_deg, inclination_deg);

        // create earth field
        mag_ef = Vector3f(intensity_gauss*1000, 0.0, 0.0);
        Matrix3f R;

        R.from_euler(0.0f, -ToRad(inclination_deg), ToRad(declination_deg));
        mag_ef = R * mag_ef;

        sem = hal.util->new_semaphore();

        have_earth_field = true;

        // form eliptical correction matrix and invert it. This is
        // needed to remove the effects of the eliptical correction
        // when calculating new offsets
        const Vector3f &diagonals = compass.get_diagonals(0);
        const Vector3f &offdiagonals = compass.get_offdiagonals(0);
        mat = Matrix3f(
            diagonals.x, offdiagonals.x, offdiagonals.y,
            offdiagonals.x,    diagonals.y, offdiagonals.z,
            offdiagonals.y, offdiagonals.z,    diagonals.z
            );
        mat.invert();

        // set initial error to field intensity
        for (uint16_t i=0; i<num_sectors; i++) {
            errors[i] = intensity_gauss*1000;
        }
        
        hal.scheduler->register_io_process(FUNCTOR_BIND_MEMBER(&CompassLearn::io_timer, void));
    }

    if (sample_available) {
        // last sample still being processed by IO thread
        return;
    }

    Vector3f field = compass.get_field(0);
    Vector3f field_change = field - last_field;
    if (field_change.length() < min_field_change) {
        return;
    }
    
    if (sem->take_nonblocking()) {
        // give a sample to the backend to process
        new_sample.field = field;
        new_sample.attitude = Vector3f(ahrs.roll, ahrs.pitch, ahrs.yaw);
        sample_available = true;
        last_field = field;
        num_samples++;
        sem->give();
    }

    if (sample_available) {
        DataFlash_Class::instance()->Log_Write("COFS", "TimeUS,OfsX,OfsY,OfsZ,Var", "Qffff",
                                               AP_HAL::micros64(),
                                               best_offsets.x,
                                               best_offsets.y,
                                               best_offsets.z,
                                               best_error);
    }

    if (!converged && num_samples > 100 && best_error < 20 && sem->take_nonblocking()) {
        // set the offsets and enable compass for EKF use
        compass.set_offsets(0, best_offsets);
        compass.set_use_for_yaw(0, true);
        converged = true;
        sem->give();
    }
}

/*
  we run the math intensive calculations in the IO thread
 */
void CompassLearn::io_timer(void)
{
    if (!sample_available) {
        return;
    }
    struct sample s;
    if (!sem->take_nonblocking()) {
        return;
    }
    s = new_sample;
    sample_available = false;
    sem->give();

    process_sample(s);
}

/*
  process a new compass sample
 */
void CompassLearn::process_sample(const struct sample &s)
{
    uint16_t besti = 0;
    float bestv = 0;

    /*
      we run through the 72 possible yaw error values, and for each
      one we calculate a value for the compass offsets if that yaw
      error is correct. 
     */
    for (uint16_t i=0; i<num_sectors; i++) {
        float yaw_err_deg = i*(360/num_sectors);

        // form rotation matrix for the euler attitude
        Matrix3f dcm;
        dcm.from_euler(s.attitude.x, s.attitude.y, wrap_2PI(s.attitude.z + radians(yaw_err_deg)));

        // calculate the field we would expect to get if this yaw error is correct
        Vector3f expected_field = dcm.transposed() * mag_ef;

        // calculate a value for the compass offsets for this yaw error
        Vector3f v1 = mat * s.field;
        Vector3f v2 = mat * expected_field;
        Vector3f offsets = (v2 - v1) + compass.get_offsets(0);
        float delta = (offsets - predicted_offsets[i]).length();

        // lowpass the predicted offsets and the error
        predicted_offsets[i] = predicted_offsets[i] * 0.95 + offsets * 0.05;
        errors[i] = errors[i] * 0.95 + delta * 0.05;

        // keep track of the current best prediction
        if (i == 0 || errors[i] < bestv) {
            besti = i;
            bestv = errors[i];
        }
    }

    if (sem->take_nonblocking()) {
        best_offsets = predicted_offsets[besti];
        best_error = bestv;
        sem->give();
    }
}
