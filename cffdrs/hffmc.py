"""
Hourly Fine Fuel Moisture Code

Calculates hourly Fine Fuel Moisture Code (FFMC) based on a calculation routine
first described in detail by Van Wagner (1977) and updated by the Canadian Forest
Service. In its simplest typical use this routine calculates a value of FFMC
based on a series of uninterrupted hourly weather observations of screen level
temperature, relative humidity, 10 m wind speed, and 1-hour rainfall.

References:
    Van Wagner, C.E. 1977. A method of computing fine fuel moisture content
    throughout the diurnal cycle. Environment Canada, Canadian Forestry Service,
    Petawawa Forest Experiment Station, Chalk River, Ontario. Information Report
    PS-X-69.
"""

from typing import Union, List, Dict, Any
import copy

from cffdrs.fire_weather_index import fire_weather_index
from cffdrs.hourly_fine_fuel_moisture_code import hourly_fine_fuel_moisture_code
from cffdrs.initial_spread_index import initial_spread_index


def hffmc(
    input: Dict[str, List[Any]],
    ffmc_old: Union[float, List[float]] = 85.0,
    time_step: float = 1.0,
    calc_step: bool = False,
    batch: bool = True,
    hourly_fwi: bool = False
) -> Union[List[float], Dict[str, List[Any]]]:
    """
    Calculate the Hourly Fine Fuel Moisture Code.

    Args:
        input: A dictionary containing input variables of hourly weather observations.
               Keys are case-insensitive. Required: temp, rh, ws, prec
        ffmc_old: Initial FFMC value (default 85)
        time_step: Time step in hours (default 1.0)
        calc_step: Whether to calculate time step between observations (default False)
        batch: Whether the computation is iterative or single step (default True)
        hourly_fwi: Whether to compute hourly ISI, FWI, and DSR (default False)

    Returns:
        Hourly FFMC values, or dataframe with additional FWI variables if hourly_fwi=True
    """
    # Convert input keys to lowercase
    input_lower = {k.lower(): v for k, v in input.items()}

    # Required columns
    required_cols = ['temp', 'rh', 'ws', 'prec']
    missing_cols = [col for col in required_cols if col not in input_lower]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Check for negative values
    for col in ['prec', 'ws', 'rh']:
        if col in input_lower:
            negative_values = [v for v in input_lower[col] if v < 0]
            if negative_values:
                print(f"Warning: {col} cannot be negative!")

    # Set up number of stations
    if batch:
        if 'id' in input_lower:
            n = len(set(input_lower['id']))
            # Check if stations have consistent data lengths
            station_counts = {}
            for station_id in input_lower['id']:
                station_counts[station_id] = station_counts.get(station_id, 0) + 1
            if len(set(station_counts.values())) > 1:
                raise ValueError("Multiple stations must have the same number of observations")
        else:
            n = 1
    else:
        n = len(input_lower['temp'])

    # Handle ffmc_old parameter
    if isinstance(ffmc_old, (int, float)):
        if n > 1:
            ffmc_old = [float(ffmc_old)] * n
        else:
            ffmc_old = [float(ffmc_old)]
    elif len(ffmc_old) == 1 and n > 1:
        ffmc_old = ffmc_old * n

    if len(ffmc_old) != n:
        raise ValueError("Number of ffmc_old values doesn't match number of weather stations")

    # Check data length consistency
    data_lengths = [len(input_lower[col]) for col in required_cols]
    if len(set(data_lengths)) > 1:
        raise ValueError("All input columns must have the same length")

    if len(input_lower['temp']) % n != 0:
        print("Warning: Input data length does not match number of weather stations")

    # Length of weather run
    n0 = len(input_lower['temp']) // n
    ffmc_values = []
    current_ffmc_old = ffmc_old.copy()

    # For each time step
    for i in range(n0):
        # Get data for all stations at this time step
        start_idx = n * i
        end_idx = n * (i + 1)

        temp_step = input_lower['temp'][start_idx:end_idx]
        rh_step = input_lower['rh'][start_idx:end_idx]
        ws_step = input_lower['ws'][start_idx:end_idx]
        prec_step = input_lower['prec'][start_idx:end_idx]

        # Handle time step calculation
        t0 = time_step
        if calc_step and i > 0:
            if 'hr' in input_lower:
                hr = input_lower['hr']
                t0 = hr[end_idx - 1] - hr[start_idx - 1] if start_idx > 0 else time_step
                if t0 == -23:
                    t0 = 1
                if t0 < 0:
                    t0 = -t0
            else:
                print("Warning: hour value is missing for calc_step!")

        # Calculate FFMC
        ffmc_step = hourly_fine_fuel_moisture_code(
            input={
                'temp': temp_step,
                'rh': rh_step,
                'ws': ws_step,
                'prec': prec_step
            },
            ffmc_old=current_ffmc_old,
            time_step=t0,
            batch=False
        )

        # Update for next iteration
        if isinstance(ffmc_step, list):
            current_ffmc_old = ffmc_step
        else:
            current_ffmc_old = [ffmc_step]

        ffmc_values.extend(ffmc_step if isinstance(ffmc_step, list) else [ffmc_step])

    # Calculate hourly FWI variables if requested
    if hourly_fwi:
        if 'bui' not in input_lower:
            print("Warning: Daily BUI is required to calculate hourly FWI")
            return ffmc_values

        bui = input_lower['bui']
        ws = input_lower['ws']

        # Calculate ISI
        isi = initial_spread_index(ffmc_values, ws, False)

        # Calculate FWI
        fwi = fire_weather_index(isi, bui)

        # Calculate DSR
        dsr = [0.0272 * (f ** 1.77) for f in fwi]

        # Return all data
        result = copy.deepcopy(input)
        result['ffmc'] = ffmc_values
        result['isi'] = isi
        result['fwi'] = fwi
        result['dsr'] = dsr
        return result
    else:
        return ffmc_values