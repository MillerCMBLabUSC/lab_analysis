#include "coordinates.h"
#include "units/angles.h"

#define _USE_MATH_DEFINES
#include <math.h>

namespace coordinates {

double great_circle(double ra0, double dec0, double ra1, double dec1)
{
    double delta_ra = ra1 - ra0;
    double y = sqrt(pow(cos(dec1)*sin(delta_ra), 2.0) + pow(cos(dec0)*sin(dec1) - sin(dec0)*cos(dec1)*cos(delta_ra), 2.0));
    double x = sin(dec0)*sin(dec1) + cos(dec0)*cos(dec1)*cos(delta_ra);
    return atan2(y, x);
}

bool angles_within(double ra0, double dec0, double ra1, double dec1, double distance)
{
    if (fabs(dec0 - dec1) >= distance) {
        return false;
    }
    return angles_within_basic(ra0, dec0, ra1, dec1, distance);
}

bool angles_within_basic(double ra0, double dec0, double ra1, double dec1, double distance)
{
    double true_distance = great_circle(ra0, dec0, ra1, dec1);
    if (true_distance >= distance) {
        return false;
    }
    return true;
}

void equatorial_to_horizontal(double ra, double dec, double lat, double lst, double& az, double& el)
{
    double h;
    double sin_dec, cos_dec, sin_lat, cos_lat, cos_H;
    double sin_el, cos_el, cos_az;

    h = lst - ra;
    if (h < 0.0)
    h += 2*M_PI;

    cos_H = cos(h);
    sin_dec = sin(dec);
    cos_dec = cos(dec);
    sin_lat = sin(lat);
    cos_lat = cos(lat);

    sin_el = sin_dec * sin_lat + (cos_dec*cos_lat*cos_H);
    el = asin(sin_el);
    cos_el = cos(el);

    cos_az = (sin_dec - sin_lat*sin_el)/(cos_lat*cos_el);
    az = acos(cos_az);

    if ((h > 0) && (h < M_PI)) az *= -1;
    while (az < 0.0)    az += 2*M_PI;
    while (az >= 360.0) az -= 2*M_PI;
}

void horizontal_to_equatorial(double az, double el, double lat, double lst, double& ra, double& dec)
{
    double sd, cosA, h1;
    double sin_lat, cos_lat, sin_el;
    double ra_temp, dec_temp;

    sin_lat = sin(lat);
    cos_lat = cos(lat);
    sin_el = sin(el);
    sd = sin_el*sin_lat + cos(el)*cos_lat*cos(az);

    dec_temp = asin(sd);

    cosA = ( sin_el - sin_lat*sd ) / ( cos_lat*cos(dec_temp) );
    h1 = acos(cosA);

    if (sin(az) > 0.0) {
    ra_temp = lst + h1 - 2*M_PI;
    } else {
    ra_temp = lst - h1;
    }

    if (ra_temp < 0.0)          ra_temp += 2*M_PI;
    else if (ra_temp >= 2*M_PI) ra_temp -= 2*M_PI;

    ra = ra_temp;
    dec = dec_temp;
}

double wrap_to_within_pi(double reference, double angle)
{
    while (angle >= reference + M_PI) {
        angle -= 2.0*M_PI;
    }
    while (angle < reference - M_PI) {
        angle += 2.0*M_PI;
    }
    return angle;
}


} // namespace coordinates
