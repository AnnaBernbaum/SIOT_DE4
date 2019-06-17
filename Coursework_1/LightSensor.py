# Adapted from Matt Hawkins BH1750 Script

import smbus
import time
import csv
import datetime
from numpy import mean

# Define some constants from the datasheet
DEVICE = 0x23  # Default device I2C address

POWER_DOWN = 0x00  # No active state
POWER_ON = 0x01  # Power on
RESET = 0x07  # Reset data register value

# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13
# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10
# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20
# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23

bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


def convertToNumber(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number. Optional parameter 'decimals'
    # will round to specified number of decimal places.
    result=(data[1] + (256 * data[0])) / 1.2
    return result


def readLight(addr=DEVICE):
    # Read data from I2C interface
    data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
    return convertToNumber(data)


def main():
    start_time = time.time()
    upload_timer = time.time()
    csvtitle = 'Data/LightLevels_1.csv'
    title_iterator = 1

    while True:

        # get the light levels of the last 5 minutes and average them. Store as an average
        five_minutes_light = []
        five_minutes = 60 * 5

        mean_timer = time.time()
        while True:
            current_light = readLight()
            mean_time_passed = time.time() - mean_timer
            five_minutes_light.append(current_light)
            time.sleep(10)  # wait 10 seconds

            if mean_time_passed > five_minutes:
                break

        lightLevel = mean(five_minutes_light)  # Average the data

        # store data in CSV
        timestamp = datetime.datetime.now()
        with open(csvtitle, 'a') as csvFile:
            writer = csv.writer(csvFile)
            row = [timestamp, lightLevel]
            writer.writerow(row)
            csvFile.close()

        # If 12 hours has passed change file title
        twelve_hours = 60 * 60 * 12
        upload_time_passed = time.time() - upload_timer
        if upload_time_passed > twelve_hours:
            upload_timer = time.time()  # reset to 0 seconds
            csvtitle = 'Data/LightLevels_' + str(title_iterator) + '.csv'  # next title
            title_iterator = title_iterator + 1


if __name__=="__main__":
    main()
