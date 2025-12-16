"""
Rate of spread at a point along the perimeter calculator

Computes the Rate of Spread at any point along the perimeter of an elliptically
shaped fire. Equations are from Wotton et. al. (2009).

Wotton, B.M., Alexander, M.E., Taylor, S.W. 2009. Updates and revisions to the 1992
Canadian forest fire behavior prediction system. Nat. Resour. Can., Can. For.
Serv., Great Lakes For. Cent., Sault Ste. Marie, Ontario, Canada. Information
Report GLC-X-10, 45p.
"""

from typing import Union, List
import math


def rate_of_spread_at_theta(
    ros: Union[float, List[float]],
    fros: Union[float, List[float]],
    bros: Union[float, List[float]],
    theta: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Rate of Spread at point theta.

    Args:
        ros: Rate of Spread (m/min)
        fros: Flank Fire Rate of Spread (m/min)
        bros: Back Fire Rate of Spread (m/min)
        theta: Angle

    Returns:
        ROSTheta: Rate of spread at point theta (m/min)
    """
    if isinstance(theta, list):
        c1 = [math.cos(t) for t in theta]
        s1 = [math.sin(t) for t in theta]
        # Handle division by zero
        c1 = [c if c != 0 else math.cos(t + 0.001) for c, t in zip(c1, theta)]
    else:
        c1 = math.cos(theta)
        s1 = math.sin(theta)
        # Handle division by zero
        c1 = c1 if c1 != 0 else math.cos(theta + 0.001)

    # Eq. 94 - Calculate the Rate of Spread at point THETA
    # Large equation, view the paper to see a better representation
    if isinstance(ros, list):
        rostheta = [0.0] * len(ros)
        for i in range(len(ros)):
            numerator = ((ros[i] - bros[i]) / (2 * c1[i]) + (ros[i] + bros[i]) / (2 * c1[i]))
            denominator_part = (fros[i] * c1[i] * math.sqrt(fros[i] * fros[i] * c1[i] * c1[i] + (ros[i] * bros[i]) * s1[i] * s1[i])
                              - ((ros[i] * ros[i] - bros[i] * bros[i]) / 4) * s1[i] * s1[i])
            denominator = (fros[i] * fros[i] * c1[i] * c1[i]
                          + ((ros[i] + bros[i]) / 2) * ((ros[i] + bros[i]) / 2) * s1[i] * s1[i])
            rostheta[i] = numerator * denominator_part / denominator
    else:
        numerator = ((ros - bros) / (2 * c1) + (ros + bros) / (2 * c1))
        denominator_part = (fros * c1 * math.sqrt(fros * fros * c1 * c1 + (ros * bros) * s1 * s1)
                          - ((ros * ros - bros * bros) / 4) * s1 * s1)
        denominator = (fros * fros * c1 * c1
                      + ((ros + bros) / 2) * ((ros + bros) / 2) * s1 * s1)
        rostheta = numerator * denominator_part / denominator

    return rostheta