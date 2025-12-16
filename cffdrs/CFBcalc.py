"""
Crown Fraction Burned Calculator

Calculate Calculate Crown Fraction Burned. To calculate CFB, we also need to calculate Critical surface intensity (CSI), and Surface fire rate of spread (RSO). The value of each of these equations can be returned to the calling function without unecessary additional calculations.

All variables names are laid out in the same manner as Forestry Canada Fire Danger Group (FCFDG) (1992). Development and Structure of the Canadian Forest Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.

References:
https://cfs.nrcan.gc.ca/publications/download-pdf/10068 Development and Structure of the Canadian Forest Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.
"""

import math

def critical_surface_intensity(FMC, CBH):
    # FIX: .FuelNF returns non-NA values from this
    # Eq. 56 (FCFDG 1992) Critical surface intensity
    if isinstance(CBH, list):
        CSI = [0.001 * (c**1.5) * (460 + 25.9 * f)**1.5 for c, f in zip(CBH, FMC)]
    else:
        CSI = 0.001 * (CBH**1.5) * (460 + 25.9 * FMC)**1.5
    return CSI

def surface_fire_rate_of_spread(CSI, SFC):
    # Eq. 57 (FCFDG 1992) Surface fire rate of spread (m/min)
    # no fuel consumption means no spread
    # RSO <- ifelse(0 == SFC, 0, CSI / (300 * SFC))
    if isinstance(CSI, list):
        RSO = [c / (300 * s) if s != 0 else 0 for c, s in zip(CSI, SFC)]
    else:
        RSO = CSI / (300 * SFC) if SFC != 0 else 0
    return RSO

def crown_fraction_burned(ROS, RSO):
    # Eq. 58 (FCFDG 1992) Crown fraction burned
    if isinstance(ROS, list):
        CFB = [1 - math.exp(-0.23 * (r - s)) if r > s else 0 for r, s in zip(ROS, RSO)]
    else:
        CFB = 1 - math.exp(-0.23 * (ROS - RSO)) if ROS > RSO else 0
    return CFB

def CFBcalc(FUELTYPE, FMC, SFC, ROS, CBH, option="CFB"):
    CSI = critical_surface_intensity(FMC, CBH)
    # Return at this point, if specified by caller
    if option == "CSI":
        return CSI
    RSO = surface_fire_rate_of_spread(CSI, SFC)
    # Return at this point, if specified by caller
    if option == "RSO":
        return RSO
    CFB = crown_fraction_burned(ROS, RSO)
    return CFB