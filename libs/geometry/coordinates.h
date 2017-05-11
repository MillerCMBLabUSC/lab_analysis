#pragma once

namespace coordinates {

double great_circle(double ra0, double dec0, double ra1, double dec1);
bool angles_within(double ra0, double dec0, double ra1, double dec1, double distance);
bool angles_within_basic(double ra0, double dec0, double ra1, double dec1, double distance);
void equatorial_to_horizontal(double ra, double dec, double lat, double lst, double &az, double &el);
void horizontal_to_equatorial(double az, double el, double lat, double lst, double& ra, double& dec);
double wrap_to_within_pi(double reference, double angle);

} // namespace coordinates
