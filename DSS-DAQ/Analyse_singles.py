import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.odr import odrpack as odr
from scipy.odr import models
from datetime import datetime
from datetime import date
from termcolor import colored, cprint
import scipy.integrate
sys.path.append("/Users/kara_lynch/Documents/CERN/Analysis/DSS_Analysis/Functions")
from DSS_Analysis import *

startTime = datetime.now()
cprint ("___________________________________________", 'blue')
print("___________________________________________")
print(time.ctime())
print("\nBeginning", colored(__file__, 'blue'))

filename = sys.argv[1]
detector = sys.argv[2]
left_limit = float(sys.argv[3])
right_limit = float(sys.argv[4])
# e.g. For fitting of single peak: ../Data/R55_04Alpha.dat 1 2500 6500 Single_Crystalball 3100 3250 3180 1400 10 0.9 4 0
# e.g. For fitting of double peak: ../Data/R55_04Alpha.dat 1 2500 6500 Double_Crystalball 5000 5250 5100 100 5150 1200 12 0.9 4 0
### Importing data from file
counts = []
with open(filename) as f:
    for i, line in enumerate(f.readlines()):
		if line[-2] == detector:
			cut_line = line[8:]
			channel = int(cut_line[:4], 16)
			timestamp = int(''.join(cut_line[5:-20].split(' ')), 16)
			if ( timestamp <= 1.1*10**9 ):
				if detector == '0':
					gamma_energy = channel*1.18554 + 0.94810
					if ( 0 <= gamma_energy <= 1500 ):
						counts.append(channel*1.18554 + 0.94810)
				if detector == '1':
					alpha_energy = (channel*0.98180 + 6.41400)
					if ( 2500 <= alpha_energy <= 6500 ):
						counts.append(channel*0.98180 + 6.41400)

if detector == '0':
	y, x = np.histogram(counts, 1500)
if detector == '1':
	y, x = np.histogram(counts, 4000)
x = x[0] + np.diff(x).cumsum()
plot_mask = np.bitwise_and(left_limit <= x, x <= right_limit)
y, x = y[plot_mask], x[plot_mask]

### Plotting the spectra

if detector == '0':
	plt.plot(x, y, '-b', label = "Ge detector")
if detector == '1':
	plt.plot(x, y, '-b', label = "Si detector")
plt.xlabel("Energy (keV)")
plt.ylabel("Counts")
plt.legend(loc='best')
plt.title(filename)
plt.show()
plt.clf()

### If no more arguments, stop the script here

if len(sys.argv) <= 5:
	sys.exit()

### If more arguments, carry on with fitting routine

fit_routine = sys.argv[5]
left_fit = float(sys.argv[6])
right_fit = float(sys.argv[7])

print("\nFitting routine: ", fit_routine)

if fit_routine == "Single_Crystalball":
	params = np.array([float(sys.argv[8]), float(sys.argv[9]), float(sys.argv[10]), float(sys.argv[11]), float(sys.argv[12]), float(sys.argv[13]) ]) # [x0, N, sigma, alpha, n, bkgnd]

if fit_routine == "Double_Crystalball":
	params = np.array([float(sys.argv[8]), float(sys.argv[9]), float(sys.argv[10]), float(sys.argv[11]), float(sys.argv[12]), float(sys.argv[13]), float(sys.argv[14]), float(sys.argv[15]) ]) # [x1, N1, x2, N2, sigma, alpha, n, bkgnd]

est_params = params

### Selecting the appropriate part of the spectrum

fit_mask = np.bitwise_and(left_fit <= x, x <= right_fit)
y_fit, x_fit = y[fit_mask], x[fit_mask]

total_counts = 0
for i in range(len(y_fit)):
	total_counts += y_fit[i]


### Plotting estimate of the fit

if detector == '0':
	plt.plot(x, y, '-b', label = "Ge detector")
if detector == '1':
	plt.plot(x, y, '-b', label = "Si detector")

superx = np.linspace(x_fit.min(), x_fit.max(), 100*len(x_fit))

if fit_routine == "Single_Crystalball":
	plt.plot(superx, Single_Crystalball(params, superx), lw=2.0, color='r')

if fit_routine == "Double_Crystalball":
	plt.plot(superx, Double_Crystalball(params, superx), lw=2.0, color='r')

plt.xlabel("Energy (keV)")
plt.ylabel("Counts")
plt.legend(loc='best')
plt.show()
plt.clf()


# Fitting the spectra with ODR

y_fit_err = np.sqrt(y_fit)

if fit_routine == "Single_Crystalball":
	model = odr.Model(Single_Crystalball)

if fit_routine == "Double_Crystalball":
	model = odr.Model(Double_Crystalball)

odr_data = odr.RealData(x_fit, y_fit)#, sy = y_fit_err)
myodr = odr.ODR(odr_data, model, beta0 = params)
myodr.set_job(fit_type = 0)
myoutput = myodr.run()

params		= myoutput.beta
params_cov	= myoutput.cov_beta

params_red_chi2	= myoutput.res_var
params_DoF		= len(x_fit)-len(params)
params_chi2		= params_red_chi2*params_DoF
if fit_routine == "Single_Crystalball":
	print("[x0, N, sigma, alpha, n, bkgnd]")
	print(params)
	print("Energy:  %.1f" % params[0])
	print("Height:  %.1f" % params[1])
	print("FWHM:    %.1f" % params[2])
	print("Bkgnd:   %.1f" % params[5])


if fit_routine == "Double_Crystalball":
	print("[x1, N1, x2, N2, sigma, alpha, n, bkgnd]")
	print(params)
	print("Energy:  %.1f\t Energy: %.2f " % (params[0], params[2]))
	print("Height:  %.1f \t Height: %.2f " % (params[1], params[3]))
	print("FWHM:    %.1f" % params[4])
	print("Bkgnd:   %.1f" % params[7])


### Plotting the fit

if detector == '0':
	plt.plot(x, y, '-b', label = "Ge detector")
if detector == '1':
	plt.plot(x, y, '-b', label = "Si detector")

if fit_routine == "Single_Crystalball":
	plt.plot(superx, Single_Crystalball(params, superx), lw=2.0, color='r')

if fit_routine == "Double_Crystalball":
	plt.plot(superx, Double_Crystalball(params, superx), lw=2.0, color='r')
plt.xlabel("Energy (keV)")
plt.ylabel("Counts")
plt.legend(loc='best')
plt.show()
plt.clf()

### Re-defining the function so the integral can be calculated - need to change this!!

def Single_Crystalball(x, x0, N, sigma, alpha, n, bkgnd):
	t = (x-x0)/sigma
	if (alpha < 0):
		t = -t
	if (t >= -abs(alpha)):
		y =  np.exp(-0.5*t*t)
	else:
		a =  ((n/abs(alpha))**n)*np.exp(-0.5*abs(alpha)*abs(alpha))
		b = n/abs(alpha) - abs(alpha)
		y = a/(b - t)**n
	return N*y

### Outputting the calculated integral counts

if fit_routine == "Single_Crystalball":
	params = tuple(params)
	integral, error = scipy.integrate.quad(Single_Crystalball, a=left_fit, b=right_fit, args=params)
	print("\nFitted integral    : %.1f +/- %f" % (integral, error))
	print("Cumulative integral: %.f " % total_counts)
	params = np.array(params)
	est_params = tuple(est_params)
	integral, error = scipy.integrate.quad(Single_Crystalball, a=left_fit, b=right_fit, args=est_params)
	print("Estimated integral : %.1f +/- %f" % (integral, error))


if fit_routine == "Double_Crystalball":
	params1 = (params[0], params[1], params[4], params[5], params[6], params[7])
	params2 = (params[2], params[3], params[4], params[5], params[6], params[7])
	integral1, error1 = scipy.integrate.quad(Single_Crystalball, a=left_fit, b=right_fit, args=params1)
	integral2, error2 = scipy.integrate.quad(Single_Crystalball, a=left_fit, b=right_fit, args=params2)
	print("\nFitted integral #1 : %.1f +/- %f" % (integral1, error1))
	print("Fitted integral #2 : %.1f +/- %f" % (integral2, error2))
	print("Cumulative integral: %.f " % total_counts)
	params1 = np.array(params1)
	params2 = np.array(params2)


### Re-defining the function back to what it was

def Single_Crystalball(params, x_array):
	x0		= params[0]
	N		= params[1]
	sigma	= params[2]
	alpha	= params[3]
	n		= params[4]
	bkgnd	= params[5]

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

### Plotting the fitted spectra again

if detector == '0':
	plt.plot(x, y, '-b', label = "Ge detector")
if detector == '1':
	plt.plot(x, y, '-b', label = "Si detector")

if fit_routine == "Single_Crystalball":
	plt.plot(superx, Single_Crystalball(params, superx), lw=2.0, color='r', label = "Peak")

if fit_routine == "Double_Crystalball":
	plt.plot(superx, Single_Crystalball(params1, superx), lw=2.0, color='r', ls='--', label = "Peak 1")
	plt.plot(superx, Single_Crystalball(params2, superx), lw=2.0, color='r', label = "Peak 2")

plt.xlabel("Energy (keV)")
plt.ylabel("Counts")
plt.legend(loc='best')
plt.show()
plt.clf()


print("___________________________________________\n")
print(colored("Time taken: ", 'blue'), (datetime.now()-startTime))
print("___________________________________________")
cprint ("___________________________________________", 'blue')
