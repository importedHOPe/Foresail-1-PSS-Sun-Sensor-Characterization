# Foresail-1 PSS Sun Sensor Characterization

Experimental characterization of the **Foresail-1 PSS Sun Sensor**, including sensor interfacing, static testing, angular characterization, data acquisition, averaging, polynomial fitting, and repeatability analysis.

The complete methodology, experimental setup, results, plots, and analysis are provided in the attached report:

- [**Read the full characterization report (PDF)**](Foresail_1_PSS_Sun_Sensor_Characterization_report.pdf)

### Reference Design

This work is based on the publicly available Foresail-1 PSS Sun Sensor design:

**Foresail-1 PSS Sun Sensor**  
https://github.com/foresail/fs1_psd_sun_sensor

The hardware design is licensed under **CERN-OHL-W-2.0**.

## Code

The `code/` directory contains the Python implementation
for acquiring and averaging PSS Sun Sensor measurements
using a Raspberry Pi 4.

- [View the code](code/sun_sensor_acquisition_rpi4.py)
- [Code documentation](code/README.md)
