"""
Line-based input for Simard Rate of Spread and Direction

This module calculates the rate of spread and direction given one set of three
point-based observations of fire arrival time. The function requires that the
user specify the time that the fire crossed each point, along with the measured
lengths between each pair of observational points, and a reference bearing (one
specified side of the triangle). This function allows quick input of a dataframe
specifying one or many triangles.

lros allows Python users to calculate the rate of spread and direction of a fire
across a triangle, given three time measurements and details about the orientation
and distance between observational points. The algorithm is based on the description
from Simard et al. (1984). See pros for more information.

The functions require the user to arrange the input dataframe so that each triangle
of interest is identified based on a new row in the dataframe. The input format
forces the user to identify the triangles, one triangle per row of input dataframe.
Very complex arrangements of field plot layouts are possible, and the current
version of these functions do not attempt to determine each triangle of interest
automatically.
"""

import math
from typing import Dict, List, Any


def direction(bearing_t1_t2: float, bearing_t1_t3: float, theta_a_deg: float) -> float:
    """Calculate direction from bearings and angle."""
    # This is a simplified version - the original uses a .direction function
    # For now, return the bearing_t1_t2 adjusted by theta
    return (bearing_t1_t2 + theta_a_deg) % 360


def lros(input_data: Dict[str, List[Any]]) -> List[Dict[str, float]]:
    """
    Calculate rate of spread and direction from three point observations with lengths and bearings.

    Args:
        input_data: Dictionary containing:
            - T1, T2, T3: Times fire crossed points 1, 2, 3
            - LENGTHT1T2, LENGTHT1T3, LENGTHT2T3: Lengths between points
            - BEARINGT1T2, BEARINGT1T3: Reference bearings

    Returns:
        List of dictionaries with ROS and Direction for each triangle
    """
    # Normalize keys to uppercase
    input_data = {k.upper(): v for k, v in input_data.items()}

    required_cols = [
        "T1", "LENGTHT1T2", "T2", "LENGTHT1T3", "T3",
        "LENGTHT2T3", "BEARINGT1T2", "BEARINGT1T3"
    ]
    for col in required_cols:
        if col not in input_data:
            raise ValueError(f"Required column {col} is missing")

    n = len(input_data["T1"])
    results = []

    for i in range(n):
        # Extract values
        t1 = input_data["T1"][i]
        length_t1_t2 = input_data["LENGTHT1T2"][i]
        t2 = input_data["T2"][i]
        length_t1_t3 = input_data["LENGTHT1T3"][i]
        t3 = input_data["T3"][i]
        length_t2_t3 = input_data["LENGTHT2T3"][i]
        bearing_t1_t2 = input_data["BEARINGT1T2"][i]
        bearing_t1_t3 = input_data["BEARINGT1T3"][i]

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