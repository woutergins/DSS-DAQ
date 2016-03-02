import sys
import numpy as np
import pandas as pd

### Loading in the data file

def load_DSS_data(filename, calibration=None):
    detector = []
    channel = []
    counts = []
    timestamp = []
    energy = []

    with open(filename) as f:
        for line in f.readlines():
            cut_line = line[8:]
            detector.append(line[-3:-1])
            channel.append(int(cut_line[:4], 16))
            timestamp.append(int(''.join(cut_line[5:-20].split(' ')), 16))
            if calibration is not None:
                try:
                    energy.append(channel[-1]*calibration[detector[-1]][0]+calibration[detector[-1]][1])
                except KeyError:
                    energy.append(0)
    detector, channel, energy = np.array(detector), np.array(channel), np.array(energy)
    data = pd.DataFrame(data=np.array([detector, channel, energy]).T, index=timestamp, columns=['Detector', 'Channel', 'Energy'])
    data[['Channel', 'Energy']] = data[['Channel', 'Energy']].astype(float)
    return data

### Defining the single-peak Gaussian function

def Single_Gaussian(params, x):
    x0          = params[0]
    intensity   = params[1]
    FWHM        = params[2]
    bkgnd       = params[3]
    return float(intensity)*np.exp(- 0.5*((x0-x)/(FWHM/2.355))**2) + bkgnd

### Defining the double-peak Gaussian function

def Double_Gaussian(params, x):
    x1          = params[0]
    intensity1  = params[1]
    x2          = params[2]
    intensity2  = params[3]
    FWHM        = params[4]
    bkgnd       = params[5]
    return float(intensity1)*np.exp(- 0.5*((x1-x)/(FWHM/2.355))**2) + float(intensity2)*np.exp(- 0.5*((x2-x)/(FWHM/2.355))**2) + bkgnd

### Defining the single-peak Crystalball function

def Single_Crystalball(params, x_array):
    x0      = params[0]
    N       = params[1]
    sigma   = params[2]
    alpha   = params[3]
    n       = params[4]
    bkgnd   = params[5]

    y_array = []
    for i in range(len(x_array)):
        x = x_array[i]
        t = (x-x0)/sigma
        if (alpha < 0):
            t = -t
        if (t >= -abs(alpha)):
            y =  np.exp(-0.5*t*t)
        else:
            a =  ((n/abs(alpha))**n)*np.exp(-0.5*abs(alpha)*abs(alpha))
            b = n/abs(alpha) - abs(alpha)
            y = a/(b - t)**n
        y_array.append(N*y + bkgnd)
    return np.array(y_array)

### Defining the double-peak Crystalball function

def Double_Crystalball(params, x_array):
    x1      = params[0]
    N1      = params[1]
    x2      = params[2]
    N2      = params[3]
    sigma   = params[4]
    alpha   = params[5]
    n       = params[6]
    bkgnd   = params[7]

    y1_array = []
    y2_array = []
    for i in range(len(x_array)):
        x = x_array[i]
        t1 = (x-x1)/sigma
        if (alpha < 0):
            t1 = -t1
        if (t1 >= -abs(alpha)):
            y1 =  np.exp(-0.5*t1*t1)
        else:
            a =  ((n/abs(alpha))**n)*np.exp(-0.5*abs(alpha)*abs(alpha))
            b = n/abs(alpha) - abs(alpha)
            y1 = a/(b - t1)**n
        y1_array.append(N1*y1)

    for i in range(len(x_array)):
        x = x_array[i]
        t2 = (x-x2)/sigma
        if (alpha < 0):
            t2 = -t2
        if (t2 >= -abs(alpha)):
            y2 =  np.exp(-0.5*t2*t2)
        else:
            a =  ((n/abs(alpha))**n)*np.exp(-0.5*abs(alpha)*abs(alpha))
            b = n/abs(alpha) - abs(alpha)
            y2 = a/(b - t2)**n
        y2_array.append(N2*y2)

    y1_array = np.array(y1_array)
    y2_array = np.array(y2_array)
    y_array = y1_array + y2_array + bkgnd
    return y_array
