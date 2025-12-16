"""
Rate of Spread Calculation and related functions.

This module contains functions for calculating rate of spread and related fire behavior metrics.
"""

import math
from typing import List

from cffdrs.C6calc import crown_fraction_burned_c6, crown_rate_of_spread_c6, intermediate_surface_rate_of_spread_c6, rate_of_spread_c6, surface_rate_of_spread_c6
from cffdrs.CFBcalc import critical_surface_intensity, crown_fraction_burned, surface_fire_rate_of_spread
from cffdrs.buildup_effect import buildup_effect


def rate_of_spread_extended(fueltype: List[str], isi: List[float], bui: List[float], fmc: List[float], sfc: List[float], pc: List[float], pdf: List[float], cc: List[float], cbh: List[float]) -> dict:
    """
    Computes the Rate of Spread prediction based on fuel type and FWI conditions.

    Args:
        fueltype: List of fuel types
        isi: List of Initial Spread Index
        bui: List of Buildup Index
        fmc: List of Foliar Moisture Content
        sfc: List of Surface Fuel Consumption
        pc: List of Percent Conifer
        pdf: List of Percent Dead Balsam Fir
        cc: List of Constant
        cbh: List of Crown Base Height

    Returns:
        Dict with ROS, CFB, CSI, RSO
    """
    # Set up data vectors
    nobui = [-1] * len(isi)
    d = [
        "C1", "C2", "C3", "C4", "C5", "C6", "C7",
        "D1", "M1", "M2", "M3", "M4", "S1", "S2", "S3", "O1A", "O1B"
    ]
    a = [
        90, 110, 110, 110, 30, 30, 45,
        30, 0, 0, 120, 100, 75, 40, 55, 190, 250
    ]
    b = [
        0.0649, 0.0282, 0.0444, 0.0293, 0.0697, 0.0800, 0.0305,
        0.0232, 0, 0, 0.0572, 0.0404, 0.0297, 0.0438, 0.0829, 0.0310, 0.0350
    ]
    c0 = [
        4.5, 1.5, 3.0, 1.5, 4.0, 3.0, 2.0,
        1.6, 0, 0, 1.4, 1.48, 1.3, 1.7, 3.2, 1.4, 1.7
    ]
    a_dict = dict(zip(d, a))
    b_dict = dict(zip(d, b))
    c0_dict = dict(zip(d, c0))

    # Calculate RSI
    rsi = []
    for i in range(len(isi)):
        ft = fueltype[i]
        if ft in ["C1", "C2", "C3", "C4", "C5", "C7", "D1", "S1", "S2", "S3"]:
            rsi_val = a_dict[ft] * (1 - math.exp(-b_dict[ft] * isi[i])) ** c0_dict[ft]
        else:
            rsi_val = -1
        rsi.append(rsi_val)

    # M1
    for i in range(len(rsi)):
        if fueltype[i] == "M1":
            ros_c2 = rate_of_spread(["C2"] * len(isi), isi, nobui, fmc, sfc, pc, pdf, cc, cbh)[i]
            ros_d1 = rate_of_spread(["D1"] * len(isi), isi, nobui, fmc, sfc, pc, pdf, cc, cbh)[i]
            rsi[i] = (pc[i] / 100 * ros_c2 + (100 - pc[i]) / 100 * ros_d1)

    # M2
    for i in range(len(rsi)):
        if fueltype[i] == "M2":
            ros_c2 = rate_of_spread(["C2"] * len(isi), isi, nobui, fmc, sfc, pc, pdf, cc, cbh)[i]
            ros_d1 = rate_of_spread(["D1"] * len(isi), isi, nobui, fmc, sfc, pc, pdf, cc, cbh)[i]
            rsi[i] = (pc[i] / 100 * ros_c2 + 0.2 * (100 - pc[i]) / 100 * ros_d1)

    # M3
    rsi_m3 = []
    for i in range(len(isi)):
        if fueltype[i] == "M3":
            rsi_m3_val = a_dict["M3"] * ((1 - math.exp(-b_dict["M3"] * isi[i])) ** c0_dict["M3"])
        else:
            rsi_m3_val = -99
        rsi_m3.append(rsi_m3_val)

    for i in range(len(rsi)):
        if fueltype[i] == "M3":
            ros_d1 = rate_of_spread(["D1"] * len(isi), isi, nobui, fmc, sfc, pc, pdf, cc, cbh)[i]
            rsi[i] = (pdf[i] / 100 * rsi_m3[i] + (1 - pdf[i] / 100) * ros_d1)

    # M4
    rsi_m4 = []
    for i in range(len(isi)):
        if fueltype[i] == "M4":
            rsi_m4_val = a_dict["M4"] * ((1 - math.exp(-b_dict["M4"] * isi[i])) ** c0_dict["M4"])
        else:
            rsi_m4_val = -99
        rsi_m4.append(rsi_m4_val)

    for i in range(len(rsi)):
        if fueltype[i] == "M4":
            ros_d1 = rate_of_spread(["D1"] * len(isi), isi, nobui, fmc, sfc, pc, pdf, cc, cbh)[i]
            rsi[i] = (pdf[i] / 100 * rsi_m4[i] + 0.2 * (1 - pdf[i] / 100) * ros_d1)

    # Grass curing
    cf = []
    for i in range(len(isi)):
        if fueltype[i] in ["O1A", "O1B"]:
            if cc[i] < 58.8:
                cf_val = 0.005 * (math.exp(0.061 * cc[i]) - 1)
            else:
                cf_val = 0.176 + 0.02 * (cc[i] - 58.8)
        else:
            cf_val = -99
        cf.append(cf_val)

    for i in range(len(rsi)):
        if fueltype[i] in ["O1A", "O1B"]:
            rsi[i] = a_dict[fueltype[i]] * ((1 - math.exp(-b_dict[fueltype[i]] * isi[i])) ** c0_dict[fueltype[i]]) * cf[i]

    # C6 special
    for i in range(len(rsi)):
        if fueltype[i] == "C6":
            rsi[i] = intermediate_surface_rate_of_spread_c6([isi[i]])[0]

    rsc = []
    for i in range(len(isi)):
        if fueltype[i] == "C6":
            rsc_val = crown_rate_of_spread_c6([isi[i]], [fmc[i]])[0]
        else:
            rsc_val = float('nan')
        rsc.append(rsc_val)

    rss = []
    for i in range(len(rsi)):
        if fueltype[i] == "C6":
            rss_val = surface_rate_of_spread_c6([rsi[i]], [bui[i]])[0]
        else:
            rss_val = buildup_effect([fueltype[i]], [bui[i]])[0] * rsi[i]
        rss.append(rss_val)

    # Calculate Critical Surface Intensity
    csi = critical_surface_intensity(fmc, cbh)
    # Calculate Surface fire rate of spread (m/min)
    rso = surface_fire_rate_of_spread(csi, sfc)
    # Calculate Crown Fraction Burned
    cfb = []
    for i in range(len(rss)):
        if fueltype[i] == "C6":
            cfb_val = crown_fraction_burned_c6([rsc[i]], [rss[i]], [rso[i]])[0]
        else:
            cfb_val = crown_fraction_burned([rss[i]], [rso[i]])[0]
        cfb.append(cfb_val)

    ros = []
    for i in range(len(rss)):
        if fueltype[i] == "C6":
            ros_val = rate_of_spread_c6([rsc[i]], [rss[i]], [cfb[i]])[0]
        else:
            ros_val = rss[i]
        if ros_val <= 0:
            ros_val = 0.000001
        ros.append(ros_val)

    return {"ROS": ros, "CFB": cfb, "CSI": csi, "RSO": rso}


def rate_of_spread(fueltype: List[str], isi: List[float], bui: List[float], fmc: List[float], sfc: List[float], pc: List[float], pdf: List[float], cc: List[float], cbh: List[float]) -> List[float]:
    """
    Computes the Rate of Spread prediction.

    Args:
        Same as rate_of_spread_extended

    Returns:
        List of ROS values
    """
    ros_vars = rate_of_spread_extended(fueltype, isi, bui, fmc, sfc, pc, pdf, cc, cbh)
    return ros_vars["ROS"]
