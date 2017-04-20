#pragma once

#include <sys/time.h>
#include <boost/thread/thread_time.hpp>
#include <limits>
#include <string>

namespace times
{
    double to_years(double time);
    double from_years(double time);
    double to_days(double time);
    double from_days(double time);
    double to_hours(double time);
    double from_hours(double time);
    double to_minutes(double time);
    double from_minutes(double time);
    double to_seconds(double time);
    double from_seconds(double time);
    double to_milliseconds(double time);
    double from_milliseconds(double time);
    std::string time_string(double time);
} // namespace timing
