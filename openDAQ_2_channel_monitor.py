import time
import serial
import matplotlib
import matplotlib.pyplot as plt
from opendaq import *
import numpy as np
from simulator import save_to_csv

OUTPUT_FILE_NAME = 'mv_log'

GAINx05 = 0  # +-12V
GAINx1 = 1  # +-4V
GAINx2 = 2  # +-2V
GAINx10 = 3  # +-0.4V
GAINx100 = 4  # +-0.04V

# Connect to the device
dq = DAQ('/dev/tty.SLAB_USBtoUART')  # Serial port of opedDAQ device
period = 1  # period = 1ms
numberPoints1 = 16  # collect 16 data-points
pinput1 = 4  # A4 as single ended input
ninput1 = 0  # negative-input=GND
nSamples1 = 20  # Mean of 20 samples per plotted data-point (10 micro-second period)
gain = GAINx10  # +-0.4V input maximum corresponding to x10 gain

numberPoints2 = 16
pinput2 = 5
ninput2 = 0
nSamples2 = 20

dq.create_stream(1, period)  # Create the Stream: data channel#, period between data-points in milliseconds
dq.setup_channel(1, numberPoints1,
                 1)  # Setup Channel: data channel#, number of data-points to collect, number of repetitions
dq.conf_channel(1, 0, pinput1, ninput1, gain,
                nSamples1)  # Configure Channel: data channel#, analog input mode, pos input, neg input, gain/max input volts, nSamples

dq.create_stream(2, period)
dq.setup_channel(2, numberPoints2, 1)
dq.conf_channel(2, 0, pinput2, ninput2, gain, nSamples2)

dq.start()  # start the stream acquisition!
data = []
channel = []

for i in range(1, max(numberPoints1, numberPoints2)):
    dq.get_stream(data, channel)

dq.stop()

print "Raw values", len(data)  # data are raw values from ADC
print "Raw channels", len(channel)  # data are raw values from ADC

gains, offset = dq.get_cal()  # use device calibration to convert raw values into voltage(mV)
print "Gains", gains  # (for openDAQ (M) only !!!)
print "Offset", offset


def convert_to_mv(raw):
    dataTemp = float(raw)
    dataTemp *= -gains[gain]
    dataTemp += offset[gain]
    dataTemp /= 100000
    return dataTemp


data_mv = []
step = 0
csv_values = ['time_ms,voltage_mv,time']
epoch = int(time.time())
friendly_time = time.strftime('%Y-%m-%d at %H.%M.%S %p')

for i in xrange(len(data)):
    dataTemp = convert_to_mv(data[i])

    data_mv.append(dataTemp)
    col_time = friendly_time
    # col_time = epoch
    csv_values.append('%s,%s,%s' % (step, dataTemp, col_time))
    step += period

print "Values in mv", data_mv
# define X values for the plot
plot_time = np.linspace(0, period * len(data_mv), len(data_mv))

# Define plot, figure and chart
# fig = plt.figure()
# plt.xlabel("Time (ms)")
# plt.ylabel("Voltage (mV)")
# plt.title("My chart")
# fig.canvas.set_window_title("Example 1")
# plt.grid(color='gray', linestyle='dashed')
# plt.plot(plot_time, data_mv)
# Finally, show our chart
# plt.show()

today = time.strftime('%Y-%m-%d')
time_stamp = time.strftime('%H:%M%p')


def find_peak(seqs):
    """
    find the peak of sine wave
    :param seqs:
    :return:
    """
    return .707 * (abs(max(seqs)) + abs(min(seqs))) / 2


def get_channels(data, channel):
    # this is mocking function need to be fixed
    c1, c2 = [], []
    for i in xrange(len(data)):
        if channel[i] == 0:
            c1.append(data[i])
        else:
            c2.append(data[i])
    return find_peak(c1), find_peak(c2)


c1, c2 = get_channels(data, channel)

c1, c2 = convert_to_mv(c1), convert_to_mv(c2)

output_data = '{0},{1},{2},{3}\n'.format(today, time_stamp, c1, c2)
"""
output file in format of "date, time, channel1, channel2"
"""
save_to_csv(OUTPUT_FILE_NAME, output_data)
