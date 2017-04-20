#include "times.h"
#include <boost/format.hpp>

namespace times {

double to_years(double time)
{
    return time / (3600.0*24.0*365.25);
}

double from_years(double time)
{
    return time * (3600.0*24.0*365.25);
}

double to_days(double time)
{
    return time / (3600.0*24.0);
}

double from_days(double time)
{
    return time * (3600.0*24.0);
}

double to_hours(double time)
{
    return time / (3600.0);
}

double from_hours(double time)
{
    return time * (3600.0);
}

double to_minutes(double time)
{
    return time / (60.0);
}

double from_minutes(double time)
{
    return time * (60.0);
}

double to_seconds(double time)
{
    return time;
}

double from_seconds(double time)
{
    return time;
}

double to_milliseconds(double time)
{
    return time * (1000.0);
}

double from_milliseconds(double time)
{
    return time / (1000.0);
}

std::string time_string(double time)
{
    std::string outstring = "";
    if (time == std::numeric_limits<double>::infinity()) {
        outstring = "inf time";
    } else if (time > from_years(999.0)) {
        outstring = (boost::format("%.0e yr") % to_years(time)).str();
    } else if (time > from_years(1.0)) {
        outstring = (boost::format("%.1f yr") % to_years(time)).str();
    } else if (time > from_days(1.0)) {
        outstring = (boost::format("%.1f dy") % to_days(time)).str();
    } else if (time > from_hours(1.0)) {
        outstring = (boost::format("%.1f hr") % to_hours(time)).str();
    } else if (time > from_minutes(1.0)) {
        outstring = (boost::format("%.1f mi") % to_minutes(time)).str();
    } else if (time > from_seconds(1.0)) {
        outstring = (boost::format("%.1f s") % to_seconds(time)).str();
    } else {
        outstring = (boost::format("%.0f ms") % to_milliseconds(time)).str();
    }
    return outstring;
}

} // namespace times
