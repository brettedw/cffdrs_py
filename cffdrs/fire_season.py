"""
Fire Season Start and End

This module calculates the start and end fire season dates for a given weather station.
The current method used in the function is based on three consecutive daily maximum
temperature thresholds (Wotton and Flannigan 1993, Lawson and Armitage 2008).
This function processes input from a single weather station.

An important aspect to consider when calculating Fire Weather Index (FWI) System variables
is a definition of the fire season start and end dates (Lawson and Armitage 2008).
If a user starts calculations on a fire season too late in the year, the FWI System
variables may take too long to reach equilibrium, thus throwing off the resulting indices.
This function presents two methods of calculating these start and end dates, adapted from
Wotton and Flannigan (1993), and Lawson and Armitage (2008). The approach taken in this
function starts the fire season after three days of maximum temperature greater than 12
degrees Celsius. The end of the fire season is determined after three consecutive days of
maximum temperature less than 5 degrees Celsius. The two temperature thresholds can be
adjusted as parameters in the function call. In regions where temperature thresholds will
not end a fire season, it is possible for the fire season to span multiple years, in this
case setting the multi_year parameter to True will allow these calculations to proceed.

This fire season length definition can also feed into the overwinter DC calculations
(overwinter_drought_code).
"""

import datetime
from typing import Dict, List, Any


def fire_season(
    input_data: Dict[str, List[Any]],
    fs_start: float = 12.0,
    fs_end: float = 5.0,
    method: str = "WF93",
    consistent_snow: bool = False,
    multi_year: bool = False
) -> List[Dict[str, Any]]:
    """
    Calculate fire season start and end dates.

    Args:
        input_data: Dictionary containing weather data with keys:
            - yr: Year of the observations (required)
            - mon: Month of the observations (required, 1-12)
            - day: Day of the observations (required, 1-31)
            - tmax: Maximum Daily Temperature (degrees C) (required)
            - snow_depth: Snow depth (optional, for LA08 method)
        fs_start: Temperature threshold to start the fire season (default=12)
        fs_end: Temperature threshold to end the fire season (default=5)
        method: Method of fire season calculation ("WF93" or "LA08", default="WF93")
        consistent_snow: Is consistent snow data in the input? (default=False)
        multi_year: Should the fire season span multiple years? (default=False)

    Returns:
        List of dictionaries with fire season start/end dates:
        - yr: Year
        - mon: Month
        - day: Day
        - fsdatetype: "start" or "end"
        - date: datetime.date object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Normalize keys to lowercase
    input_data = {k.lower(): v for k, v in input_data.items()}

    # Validate required fields
    required_fields = ["yr", "mon", "day", "tmax"]
    for field in required_fields:
        if field not in input_data:
            raise ValueError(f"{field} is required for fire_season calculation")

    yr = input_data["yr"]
    mon = input_data["mon"]
    day = input_data["day"]
    tmax = input_data["tmax"]

    # Validate month and day ranges
    if not all(1 <= m <= 12 for m in mon):
        raise ValueError("Month values must be between 1 and 12")
    if not all(1 <= d <= 31 for d in day):
        raise ValueError("Day values must be between 1 and 31")

    method = method.upper()
    if method not in ["WF93", "LA08"]:
        raise ValueError(f"Method '{method}' is not supported. Use 'WF93' or 'LA08'")

    n0 = len(tmax)
    season_active = False
    season_start_end = []

    if method == "WF93":
        # Wotton & Flannigan 1993 fire season calculation method
        for k in range(3, n0):  # Start from index 3 (4th element, 0-based)
            # Check if we should start a fire season
            if (not season_active and
                all(t > fs_start for t in tmax[k-3:k])):  # Last 3 days > fs_start
                season_active = True
                the_day = day[k]
                # Adjust for January 4th start
                if not multi_year and mon[k] == 1 and day[k] == 4:
                    the_day = day[k-3]
                season_start_end.append({
                    "yr": yr[k],
                    "mon": mon[k],
                    "day": the_day,
                    "fsdatetype": "start"
                })

            # Check if we should end a fire season
            if (season_active and
                all(t < fs_end for t in tmax[k-3:k])):  # Last 3 days < fs_end
                season_active = False
                season_start_end.append({
                    "yr": yr[k],
                    "mon": mon[k],
                    "day": day[k],
                    "fsdatetype": "end"
                })

    elif method == "LA08":
        # Lawson and Armitage 2008 method
        if consistent_snow:
            if "snow_depth" not in input_data:
                raise ValueError("Snow depth is required for LA08 method with consistent_snow=True")
            snow_depth = input_data["snow_depth"]

            for k in range(3, n0):
                # Start season when last 3 days are snow-free
                if (not season_active and
                    all(sd <= 0 for sd in snow_depth[k-2:k+1])):  # k-2 to k inclusive
                    season_active = True
                    the_day = day[k]
                    if not multi_year and mon[k] == 1 and day[k] == 4:
                        the_day = day[k-3]
                    season_start_end.append({
                        "yr": yr[k],
                        "mon": mon[k],
                        "day": the_day,
                        "fsdatetype": "start"
                    })

                # End season if snow on ground or (December and temp < fs_end)
                if season_active and (
                    snow_depth[k] > 0 or
                    (mon[k] == 12 and all(t < fs_end for t in tmax[k-2:k+1]))
                ):
                    season_active = False
                    season_start_end.append({
                        "yr": yr[k],
                        "mon": mon[k],
                        "day": day[k],
                        "fsdatetype": "end"
                    })
        else:
            # Fall back to WF93 if no consistent snow data
            return fire_season(input_data, fs_start, fs_end, "WF93", False, multi_year)

    # Add date objects and remove duplicates
    for entry in season_start_end:
        try:
            entry["date"] = datetime.date(entry["yr"], entry["mon"], entry["day"])
        except ValueError:
            # Invalid date, skip
            continue

    # Remove entries with duplicate dates
    seen_dates = set()
    filtered_results = []
    for entry in season_start_end:
        date_key = (entry["yr"], entry["mon"], entry["day"], entry["fsdatetype"])
        if date_key not in seen_dates:
            seen_dates.add(date_key)
            filtered_results.append(entry)

    return filtered_results


# Alias for backward compatibility
fireSeason = fire_season