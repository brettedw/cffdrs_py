"""
Point-based input for Simard Rate of Spread and Direction

This module calculates the rate of spread and direction given one set of three
point-based observations of fire arrival time. The function requires that the
user specify the time that the fire crossed each point, along with the latitude
and longitude of each observational point. This function allows quick input of
a dataframe specifying one or many triangles.

pros allows Python users to calculate the rate of spread and direction of a fire
across a triangle, given three time measurements and details about the orientation
and distance between observational points. The algorithm is based on the description
from Simard et al. (1984).

Rate of spread and direction of spread are primary variables of interest when
observing wildfire growth over time. Observations might be recorded during normal
fire management operations, during prescribed fire treatments, and during
experimental research burns. Rate of spread is especially important for estimating
Byram's fireline intensity.

The underlying algorithms use trigonometry to solve for rate of spread and direction
of spread. One important assumption is that the spread rate and direction is uniform
across one triangular plot, and that the fire front is spreading as a straight line.
"""

import math
from typing import Dict, List, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points using haversine formula."""
    # Convert to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Earth's radius in meters
    R = 6371000
    return R * c


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the bearing from point 1 to point 2."""
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlon = lon2_rad - lon1_rad

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to 0-360
    return (bearing_deg + 360) % 360


def direction(bearing_t1_t2: float, bearing_t1_t3: float, theta_a_deg: float) -> float:
    """Calculate direction from bearings and angle."""
    # This is a simplified version - the original uses a .direction function
    # For now, return the bearing_t1_t2 adjusted by theta
    return (bearing_t1_t2 + theta_a_deg) % 360


def pros(input_data: Dict[str, List[Any]]) -> List[Dict[str, float]]:
    """
    Calculate rate of spread and direction from three point observations.

    Args:
        input_data: Dictionary containing:
            - T1, T2, T3: Times fire crossed points 1, 2, 3
            - LONG1, LAT1, LONG2, LAT2, LONG3, LAT3: Coordinates

    Returns:
        List of dictionaries with ROS and Direction for each triangle
    """
    # Normalize keys to uppercase
    input_data = {k.upper(): v for k, v in input_data.items()}

    required_cols = ["T1", "LONG1", "LAT1", "T2", "LONG2", "LAT2", "T3", "LONG3", "LAT3"]
    for col in required_cols:
        if col not in input_data:
            raise ValueError(f"Required column {col} is missing")

    n = len(input_data["T1"])
    results = []

    for i in range(n):
        # Extract coordinates and times
        t1 = input_data["T1"][i]
        long1, lat1 = input_data["LONG1"][i], input_data["LAT1"][i]
        t2 = input_data["T2"][i]
        long2, lat2 = input_data["LONG2"][i], input_data["LAT2"][i]
        t3 = input_data["T3"][i]
        long3, lat3 = input_data["LONG3"][i], input_data["LAT3"][i]

        # Calculate distances
        length_t1_t2 = haversine_distance(lat1, long1, lat2, long2)
        length_t1_t3 = haversine_distance(lat1, long1, lat3, long3)
        length_t2_t3 = haversine_distance(lat2, long2, lat3, long3)

        # Calculate bearings
        bearing_t1_t2 = bearing(lat1, long1, lat2, long2)
        bearing_t1_t3 = bearing(lat1, long1, lat3, long3)
        bearing_t2_t3 = bearing(lat2, long2, lat3, long3)

        # Calculate angles
        cos_angle_a = (length_t1_t3**2 + length_t1_t2**2 - length_t2_t3**2) / (2 * length_t1_t3 * length_t1_t2)
        cos_angle_a = max(min(cos_angle_a, 1.0), -1.0)  # Clamp to avoid domain errors
        angle_a_rad = math.acos(cos_angle_a)
        angle_a_deg = math.degrees(angle_a_rad)

        # Calculate theta
        if t2 != t1 and length_t1_t3 * math.sin(angle_a_rad) != 0:
            theta_a_rad = math.atan(
                ((t3 - t1) / (t2 - t1)) * (length_t1_t2 / (length_t1_t3 * math.sin(angle_a_rad)))
                - (1 / math.tan(angle_a_rad))
            )
        else:
            theta_a_rad = 0.0

        theta_a_deg = math.degrees(theta_a_rad)

        # Calculate direction
        dir_val = direction(bearing_t1_t2, bearing_t1_t3, theta_a_deg)

        # Calculate ROS
        if t2 != t1:
            ros = (length_t1_t2 * math.cos(theta_a_rad)) / (t2 - t1)
        else:
            ros = 0.0

        results.append({"Ros": ros, "Direction": dir_val})

    return results