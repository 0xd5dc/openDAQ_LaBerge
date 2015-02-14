import time
import serial
import matplotlib
import matplotlib.pyplot as plt
from opendaq import *
import numpy as np

GAINx05 = 0  # +-12V
GAINx1 = 1  # +-4V
GAINx2 = 2  # +-2V
GAINx10 = 3  # +-0.4V
GAINx100 = 4  # +-0.04V

# Connect to the device
dq = DAQ('/dev/tty.SLAB_USBtoUART')  #Serial port of opedDAQ device
period = 6  #period = 6ms
numberPoints1 = 40  #collect 40 data-points
pinput1 = 4  #A4 as single ended input
ninput1 = 0  #negative-input=GND
nSamples1 = 20  #Mean of 20 samples per plotted data-point (10 micro-second period)
gain = GAINx10  #+-0.4V input maximum corresponding to x10 gain

numberPoints2 = 40
pinput2 = 5
ninput2 = 0
nSamples2 = 20

dq.create_stream(1, period)  #Create the Stream: data channel#, period between data-points in milliseconds
dq.setup_channel(1, numberPoints1,
                 1)  #Setup Channel: data channel#, number of data-points to collect, number of repetitions
dq.conf_channel(1, 0, pinput1, ninput1, gain,
                nSamples1)  #Configure Channel: data channel#, analog input mode, pos input, neg input, gain/max input volts, nSamples

dq.create_stream(2, period)
dq.setup_channel(2, numberPoints2, 1)
dq.conf_channel(2, 0, pinput2, ninput2, gain, nSamples2)

dq.start()  #start the stream acquisition!
data = []
channel = []
while True:
    result = dq.get_stream(data, channel)
    if result == 1:  #data available
        print "New data received -> n Points = ", len(data)
    elif result == 3:  #stop
        print "Stop received"
        break

print "Raw values", data  #data are raw values from ADC

gains, offset = dq.get_cal()  #use device calibration to convert raw values into voltage(mV)
print "Gains", gains  #(for openDAQ (M) only !!!)
print "Offset", offset

data_mv = []
step = 0
csv_values = ['time_ms,voltage_mv,time']
epoch = int(time.time())
friendly_time = time.strftime('%Y-%m-%d at %H.%M.%S %p')
for i in range(len(data)):
    dataTemp = float(data[i])
    dataTemp *= -gains[gain]
    dataTemp += offset[gain]
    dataTemp /= 100000
    data_mv.append(dataTemp)
    col_time = friendly_time
    #col_time = epoch
    csv_values.append('%s,%s,%s' % (step, dataTemp, col_time))
    step += period
print "Values in mv", data_mv
#define X values for the plot
plot_time = np.linspace(0, period * len(data_mv), len(data_mv))

#Define plot, figure and chart
fig = plt.figure()
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (mV)")
plt.title("My chart")
fig.canvas.set_window_title("Example 1")
plt.grid(color='gray', linestyle='dashed')
plt.plot(plot_time, data_mv)
#Finally, show our chart
plt.show()

#Open a CSV file and write values to it
file_name = friendly_time + '.csv'
with open(file_name, 'w') as csv_file:
    csv_file.write('\n'.join(csv_values))
