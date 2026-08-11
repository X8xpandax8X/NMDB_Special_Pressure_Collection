import pandas as pd
import requests
import re
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Dowload data from 1 station
def fetch_single_station(station, start_dt, end_dt, dtype):
    base_url = "https://www.nmdb.eu/nest/draw_graph.php"

    params = [
        ('formchk', '1'),
        ('stations[]', station),
        ('tabchoice', 'revori'),
        ('dtype', dtype),
        ('tresolution', '0'),
        ('yunits', '0'),
        ('date_choice', 'bydate'),
        ('start_day', str(start_dt.day)),
        ('start_month', str(start_dt.month)),
        ('start_year', str(start_dt.year)),
        ('start_hour', str(start_dt.hour)),
        ('start_min', str(start_dt.minute)),
        ('end_day', str(end_dt.day)),
        ('end_month', str(end_dt.month)),
        ('end_year', str(end_dt.year)),
        ('end_hour', str(end_dt.hour)),
        ('end_min', str(end_dt.minute)),
        ('output', 'ascii')
    ]

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Error fetching {station} ({dtype})")
        return None

    lines = response.text.splitlines()

    # filter
    data_lines = [line.strip() for line in lines if re.match(r'^\d{4}-\d{2}-\d{2}', line.strip())]

    if not data_lines:
        return None

    parsed_rows = []
    for line in data_lines:
        clean_line = line.replace(';', ' ')# delete semicolon
        tokens = clean_line.split()

        if len(tokens) >= 3:
            try:
                val = float(tokens[2])
            except ValueError:
                val = None
            parsed_rows.append([tokens[0], tokens[1], val])
        elif len(tokens) == 2:
            parsed_rows.append([tokens[0], tokens[1], None])

    if not parsed_rows:
        return None

    df = pd.DataFrame(parsed_rows, columns=['date', 'time', station])

    # make timestamp
    df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    return df[['timestamp', station]]

# make a table of all station
def build_multi_station_table(stations_list, start_dt, end_dt, dtype):
    main_df = None

    for station in stations_list:
        print(f"[{dtype}] Dowloading: {station}...")
        df_station = fetch_single_station(station, start_dt, end_dt, dtype)

        if df_station is not None:
            if main_df is None:
                main_df = df_station
            else:
                main_df = pd.merge(main_df, df_station, on='timestamp', how='outer')

    if main_df is not None:
        main_df = main_df.sort_values('timestamp').reset_index(drop=True)
        main_df.insert(0, 'Date', main_df['timestamp'].dt.strftime('%Y-%m-%d'))

    return main_df

if __name__ == "__main__":
    my_stations = ['APTY', 'BRBG', 'CAPS', 'FSMT', 'INVK', 'KERG', 'MCMU', 'MWSN', 'NAIN', 'OULU', 'PWNK', 'TERA', 'THUL']
    start_time = pd.Timestamp("2006-12-13 00:00:00")
    end_time = pd.Timestamp("2006-12-13 11:59:00")

    print("=== ดึงข้อมูลตาราง Pressure Corrected ===")
    df_corrected = build_multi_station_table(my_stations, start_time, end_time, dtype="corr_for_pressure")
    display(df_corrected)

    print("=== ดึงข้อมูลตาราง  Uncorrected ===")
    df_uncorrected = build_multi_station_table(my_stations, start_time, end_time, dtype="uncorrected")
    display(df_uncorrected)

    print("=== ดึงข้อมูลตาราง  Pressure ===")
    df_pressure = build_multi_station_table(my_stations, start_time, end_time, dtype="pressure_mbar")
    display(df_pressure)