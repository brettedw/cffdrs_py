"""
Moisture content Calculation for use in the GFMC calculation
"""

from typing import Union, List
import math


def grass_fuel_moisture(
    temp: Union[float, List[float]],
    rh: Union[float, List[float]],
    ws: Union[float, List[float]],
    prec: Union[float, List[float]],
    isol: Union[float, List[float]],
    gfmc_old: Union[float, List[float]],
    time_step: float = 1,
    ro_fl: float = 0.3
) -> Union[float, List[float]]:
    """
    Calculate moisture content for use in the GFMC calculation.

    Args:
        temp: Temperature
        rh: Relative Humidity
        ws: Wind Speed
        prec: Precipitation
        isol: Insolation
        gfmc_old: Yesterdays Grass Foliar Moisture Content
        time_step: Time step (hour) [default 1 hour]
        ro_fl: The nominal fuel load of the fine fuel layer, default is 0.3 kg/m^2

    Returns:
        MC0: Moisture content
    """
    # Eq. 13 - Calculate previous moisture code
    if isinstance(gfmc_old, list):
        mc_old = [250.0 * (101 - g) / (59.5 + g) for g in gfmc_old]
    else:
        mc_old = 250.0 * (101 - gfmc_old) / (59.5 + gfmc_old)

    # Eq. 11 - Calculate the moisture content of the layer in % after rainfall
    if isinstance(prec, list):
        mcr = [m + 100 * (p / ro_fl) if p > 0 else m for m, p in zip(mc_old, prec)]
    else:
        mcr = mc_old + 100 * (prec / ro_fl) if prec > 0 else mc_old

    # Constrain to 250
    if isinstance(mcr, list):
        mcr = [min(m, 250) for m in mcr]
    else:
        mcr = min(mcr, 250)

    if isinstance(mcr, list):
        mc_old = mcr
    else:
        mc_old = mcr

    # Eq. 2 - Calculate Fuel temperature
    if isinstance(temp, list):
        tf = [t + 35.07 * i * math.exp(-0.06215 * w) for t, i, w in zip(temp, isol, ws)]
    else:
        tf = temp + 35.07 * isol * math.exp(-0.06215 * ws)

    # Eq. 3 - Calculate Saturation Vapour Pressure (Baumgartner et a. 1982)
    if isinstance(temp, list):
        es_t = [6.107 * 10 ** (7.5 * t / (237 + t)) for t in temp]
    else:
        es_t = 6.107 * 10 ** (7.5 * temp / (237 + temp))

    # Eq. 3 for Fuel temperature
    if isinstance(tf, list):
        es_tf = [6.107 * 10 ** (7.5 * t / (237 + t)) for t in tf]
    else:
        es_tf = 6.107 * 10 ** (7.5 * tf / (237 + tf))

    # Eq. 4 - Calculate Fuel Level Relative Humidity
    if isinstance(rh, list):
        rh_f = [r * es_t[i] / es_tf[i] for i, r in enumerate(rh)]
    else:
        rh_f = rh * es_t / es_tf

    # Eq. 7 - Calculate Equilibrium Moisture Content for Drying phase
    if isinstance(rh_f, list):
        emc_d = [(1.62 * r ** 0.532 + 13.7 * math.exp((r - 100) / 13.0)
                 + 0.27 * (26.7 - t) * (1 - math.exp(-0.115 * r)))
                for r, t in zip(rh_f, tf)]
    else:
        emc_d = (1.62 * rh_f ** 0.532 + 13.7 * math.exp((rh_f - 100) / 13.0)
                + 0.27 * (26.7 - tf) * (1 - math.exp(-0.115 * rh_f)))

    # Eq. 7 - Calculate Equilibrium Moisture Content for Wetting phase
    if isinstance(rh_f, list):
        emc_w = [(1.42 * r ** 0.512 + 12.0 * math.exp((r - 100) / 18.0)
                 + 0.27 * (26.7 - t) * (1 - math.exp(-0.115 * r)))
                for r, t in zip(rh_f, tf)]
    else:
        emc_w = (1.42 * rh_f ** 0.512 + 12.0 * math.exp((rh_f - 100) / 18.0)
                + 0.27 * (26.7 - tf) * (1 - math.exp(-0.115 * rh_f)))

    # RH in terms of RH/100 for desorption
    if isinstance(mc_old, list):
        rf = [r / 100 if m > emc_d[i] else r for i, (r, m) in enumerate(zip(rh_f, mc_old))]
        # RH in terms of 1-RH/100 for absorption
        rf = [(100 - r) / 100 if m < emc_w[i] else r for i, (r, m) in enumerate(zip(rf, mc_old))]
    else:
        rf = rh_f / 100 if mc_old > emc_d else rh_f
        # RH in terms of 1-RH/100 for absorption
        rf = (100 - rh_f) / 100 if mc_old < emc_w else rf

    # Eq. 10 - Calculate Inverse Response time of grass (hours)
    if isinstance(tf, list):
        k_grass = [0.389633 * math.exp(0.0365 * t) * (0.424 * (1 - r ** 1.7) + 0.0694 *
                   math.sqrt(w) * (1 - r ** 8)) for t, r, w in zip(tf, rf, ws)]
    else:
        k_grass = 0.389633 * math.exp(0.0365 * tf) * (0.424 * (1 - rf ** 1.7) + 0.0694 *
                  math.sqrt(ws) * (1 - rf ** 8))

    # Fuel is drying, calculate Moisture Content
    if isinstance(mc_old, list):
        mc0 = [emc_d[i] + (m - emc_d[i]) * math.exp(-1.0 * math.log(10.0) * k * time_step)
               if m > emc_d[i] else m for i, (m, k) in enumerate(zip(mc_old, k_grass))]
    else:
        mc0 = (emc_d + (mc_old - emc_d) * math.exp(-1.0 * math.log(10.0) * k_grass * time_step)
               if mc_old > emc_d else mc_old)

    # Fuel is wetting, calculate moisture content
    if isinstance(mc0, list):
        mc0 = [emc_w[i] + (m - emc_w[i]) * math.exp(-1.0 * math.log(10.0) * k * time_step)
               if m < emc_w[i] else m for i, (m, k) in enumerate(zip(mc0, k_grass))]
    else:
        mc0 = (emc_w + (mc0 - emc_w) * math.exp(-1.0 * math.log(10.0) * k_grass * time_step)
               if mc0 < emc_w else mc0)

    return mc0