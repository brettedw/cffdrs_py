"""
C-6 Conifer Plantation Fire Spread Calculator

Calculate c6 (Conifer plantation) Fire Spread. C6 is a special case, and thus has it's own function. To calculate C6 fire spread, this function also calculates and can return ROS, CFB, RSC, or RSI by specifying in the option parameter.

All variables names are laid out in the same manner as Forestry Canada Fire Danger Group (FCFDG) (1992). Development and Structure of the Canadian Forest Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.

References:
https://cfs.nrcan.gc.ca/publications/download-pdf/10068 Development and Structure of the Canadian Forest Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.
"""

import math

from cffdrs.CFBcalc import critical_surface_intensity, crown_fraction_burned, surface_fire_rate_of_spread
from cffdrs.buildup_effect import buildup_effect

def intermediate_surface_rate_of_spread_c6(ISI):
    # Eq. 62 (FCFDG 1992) Intermediate surface fire spread rate
    RSI = 30 * (1 - math.exp(-0.08 * ISI))**3.0
    return RSI

def surface_rate_of_spread_c6(RSI, BUI):
    # Eq. 63 (FCFDG 1992) Surface fire spread rate (m/min)
    RSS = RSI * buildup_effect("C6", BUI)
    return RSS

def crown_rate_of_spread_c6(ISI, FMC):
    # Average foliar moisture effect
    FMEavg = 0.778
    # Eq. 59 (FCFDG 1992) Crown flame temperature (degrees K)
    tt = 1500 - 2.75 * FMC
    # Eq. 60 (FCFDG 1992) Head of ignition (kJ/kg)
    H = 460 + 25.9 * FMC
    # Eq. 61 (FCFDG 1992) Average foliar moisture effect
    FME = ((1.5 - 0.00275 * FMC)**4.0) / (460 + 25.9 * FMC) * 1000
    # Eq. 64 (FCFDG 1992) Crown fire spread rate (m/min)
    RSC = 60 * (1 - math.exp(-0.0497 * ISI)) * FME / FMEavg
    return RSC

def crown_fraction_burned_c6(RSC, RSS, RSO):
    CFB = crown_fraction_burned(RSS, RSO) if (RSC > RSS and RSS > RSO) else 0
    return CFB

def rate_of_spread_c6(RSC, RSS, CFB):
    # Eq. 65 (FCFDG 1992) Calculate Rate of spread (m/min)
    ROS = RSS + (CFB) * (RSC - RSS) if RSC > RSS else RSS
    return ROS

def C6calc(FUELTYPE, ISI, BUI, FMC, SFC, CBH, ROS, CFB, RSC, option="CFB"):
    # Note: this function is deprecated in the R version
    RSI = intermediate_surface_rate_of_spread_c6(ISI)
    # Return at this point, if specified by caller
    if option == "RSI":
        return RSI
    RSC = crown_rate_of_spread_c6(ISI, FMC)
    # Return at this point, if specified by caller
    if option == "RSC":
        return RSC
    RSS = surface_rate_of_spread_c6(RSI, BUI)
    CSI = critical_surface_intensity(FMC, CBH)
    RSO = surface_fire_rate_of_spread(CSI, SFC)
    # Crown Fraction Burned
    CFB = crown_fraction_burned_c6(RSC, RSS, RSO)
    # Return at this point, if specified by caller
    if option == "CFB":
        return CFB
    ROS = rate_of_spread_c6(RSC, RSS, CFB)
    return ROS