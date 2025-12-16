"""
Direction definer

New DIRECTION function to determine clockwise or counter-clockwise "interpretation".
"""

from typing import Union, List


def direction(
    bearing_t1_t2: Union[float, List[float]],
    bearing_t1_t3: Union[float, List[float]],
    theta_adeg: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Determine direction interpretation.

    Args:
        bearing_t1_t2: Bearing between T1 and T2
        bearing_t1_t3: Bearing between T1 and T3
        theta_adeg: Direction

    Returns:
        DIR: A direction in degrees
    """
    if isinstance(bearing_t1_t2, list):
        n = len(bearing_t1_t2)
        dir_result = [float('nan')] * n

        for i in range(n):
            t1t2 = bearing_t1_t2[i]
            t1t3 = bearing_t1_t3[i]
            theta = theta_adeg[i] if isinstance(theta_adeg, list) else theta_adeg

            # Case 1: Both bearings positive, T1T2 > T1T3
            if t1t2 > 0 and t1t3 > 0 and t1t2 > t1t3:
                dir_result[i] = t1t2 - theta
            # Case 2: Both bearings positive, T1T2 < T1T3
            elif t1t2 > 0 and t1t3 > 0 and t1t2 < t1t3:
                dir_result[i] = t1t2 + theta
            # Case 3: Both bearings negative, T1T2 > T1T3
            elif t1t2 < 0 and t1t3 < 0 and t1t2 > t1t3:
                dir_result[i] = t1t2 - theta
            # Case 4: Both bearings negative, T1T2 < T1T3
            elif t1t2 < 0 and t1t3 < 0 and t1t2 < t1t3:
                dir_result[i] = t1t2 + theta
            # Case 5: T1T2 positive, T1T3 negative, specific range
            elif (t1t2 > 0 and t1t2 < 90 and t1t3 < 0 and t1t3 > -90):
                dir_result[i] = t1t2 - theta
            # Case 6: T1T2 negative, T1T3 positive, specific range
            elif (t1t2 < 0 and t1t2 > -90 and t1t3 > 0 and t1t3 < 90):
                dir_result[i] = t1t2 + theta
            # Case 7: T1T2 > 90, T1T3 < -90, check for 180 degree wrap
            elif (t1t2 > 90 and t1t3 < -90 and t1t2 + theta > 180):
                dir_result[i] = t1t2 + theta - 360
            elif (t1t2 > 90 and t1t3 < -90 and t1t2 + theta < 180):
                dir_result[i] = t1t2 + theta
            # Case 8: T1T2 < -90, T1T3 > 90, check for -180 degree wrap
            elif (t1t2 < -90 and t1t3 > 90 and t1t2 - theta < -180):
                dir_result[i] = t1t2 - theta + 360
            elif (t1t2 < -90 and t1t3 > 90 and t1t2 - theta > -180):
                dir_result[i] = t1t2 - theta

            # Additional constraints
            if dir_result[i] < -180:
                dir_result[i] += 360
            if dir_result[i] > 180:
                dir_result[i] -= 360
    else:
        t1t2 = bearing_t1_t2
        t1t3 = bearing_t1_t3
        theta = theta_adeg

        dir_result = float('nan')

        # Case 1: Both bearings positive, T1T2 > T1T3
        if t1t2 > 0 and t1t3 > 0 and t1t2 > t1t3:
            dir_result = t1t2 - theta
        # Case 2: Both bearings positive, T1T2 < T1T3
        elif t1t2 > 0 and t1t3 > 0 and t1t2 < t1t3:
            dir_result = t1t2 + theta
        # Case 3: Both bearings negative, T1T2 > T1T3
        elif t1t2 < 0 and t1t3 < 0 and t1t2 > t1t3:
            dir_result = t1t2 - theta
        # Case 4: Both bearings negative, T1T2 < T1T3
        elif t1t2 < 0 and t1t3 < 0 and t1t2 < t1t3:
            dir_result = t1t2 + theta
        # Case 5: T1T2 positive, T1T3 negative, specific range
        elif (t1t2 > 0 and t1t2 < 90 and t1t3 < 0 and t1t3 > -90):
            dir_result = t1t2 - theta
        # Case 6: T1T2 negative, T1T3 positive, specific range
        elif (t1t2 < 0 and t1t2 > -90 and t1t3 > 0 and t1t3 < 90):
            dir_result = t1t2 + theta
        # Case 7: T1T2 > 90, T1T3 < -90, check for 180 degree wrap
        elif (t1t2 > 90 and t1t3 < -90 and t1t2 + theta > 180):
            dir_result = t1t2 + theta - 360
        elif (t1t2 > 90 and t1t3 < -90 and t1t2 + theta < 180):
            dir_result = t1t2 + theta
        # Case 8: T1T2 < -90, T1T3 > 90, check for -180 degree wrap
        elif (t1t2 < -90 and t1t3 > 90 and t1t2 - theta < -180):
            dir_result = t1t2 - theta + 360
        elif (t1t2 < -90 and t1t3 > 90 and t1t2 - theta > -180):
            dir_result = t1t2 - theta

        # Additional constraints
        if dir_result < -180:
            dir_result += 360
        if dir_result > 180:
            dir_result -= 360

    return dir_result