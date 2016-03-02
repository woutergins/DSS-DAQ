import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
from inputs import *

startTime = datetime.now()
print("___________________________________________")
print(time.ctime())

filename = sys.argv[1]

### Importing data from file
counts = []
alpha_timestamp = []
gamma_timestamp = []
alpha_energy = []
gamma_energy = []

with open(filename) as f:
	for i, line in enumerate(f.readlines()):
		cut_line = line[8:]
		if line[-3:-1] == '41': # Silicon detector
			channel = int(cut_line[:4], 16)
			alpha_energy_cali = channel*0.98180 + 6.41400
			if ( alpha_range_lower <= alpha_energy_cali <= alpha_range_upper ):
				timestamp = int(''.join(cut_line[5:-20].split(' ')), 16)
				if ( timestamp <= 1.1*10**9 ):
					alpha_energy.append(alpha_energy_cali)
					alpha_timestamp.append(timestamp)
		if line[-3:-1] == '40': # Germanium detector
			channel = int(cut_line[:4], 16)
			gamma_energy_cali = channel*1.18554 + 0.94810
			if ( gamma_range_lower <= gamma_energy_cali <= gamma_range_upper ):
				timestamp = int(''.join(cut_line[5:-20].split(' ')), 16)
				if ( timestamp <= 1.1*10**9 ):
					gamma_energy.append(gamma_energy_cali)
					gamma_timestamp.append(timestamp)

alphas	= np.column_stack((alpha_energy, alpha_timestamp, np.ones(len(alpha_energy))))
gammas	= np.column_stack((gamma_energy, gamma_timestamp, np.zeros(len(gamma_energy))))
data	= np.vstack((alphas, gammas)) #[Energy, Time, Channel]

# Plot histogram of alpha events

plt.hist(alphas[:,0], bins=2000, histtype='step', color='b')
plt.xlabel("Alpha energy (keV)")
plt.ylabel("Counts")
plt.show()
plt.clf()

# Plot histogram of gamma events
plt.hist(gammas[:,0], bins=1500, histtype='step', color='b')
plt.xlabel("Gamma energy (keV)")
plt.ylabel("Counts")
plt.show()
plt.clf()
# Sort all data by time
data = data[data[:,1].argsort()]
# Calculate time between successive events
time_delta = data[1:,1] - data[:-1,1]
# Plot histogram of time_delta
plt.hist(time_delta, bins=10000, histtype='step', color='b')
plt.xlabel("Time between sucessive events")
plt.ylabel("Counts")
plt.show()
plt.clf()
# Create coincidence array [Energy, Channel, Energy, Channel, Time_delta]
coincidence = np.column_stack((data[:-1,0], data[:-1,2], data[1:,0], data[1:,2], time_delta ))
# Gating on alpha energy
time_cut			= coincidence[(coincidence[:,4] >= 0) & (coincidence[:,4] <= coinc_window)]
all_gammas			= time_cut[(time_cut[:,3] == 0)]
coinc_with_alpha	= all_gammas[(all_gammas[:,0] >= alpha_gate_lower) & (all_gammas[:,0] <= alpha_gate_upper) & (all_gammas[:,1] == 1)]
prompt_coincs		= coinc_with_alpha[(coinc_with_alpha[:,4] >= t_start) & (coinc_with_alpha[:,4] <= t_finish)]
print "Gammas in prompt coinc with alphas: %i [%.f < Ea < %.f]" % (len(prompt_coincs), alpha_gate_lower, alpha_gate_upper)
#plt.hist(all_gammas[:,2], bins=1500, histtype='stepfilled', color='b', label= "All gammas")
plt.hist(coinc_with_alpha[:,2], bins=500, histtype='step', color='b', label= "Coinc with alpha")
plt.hist(prompt_coincs[:,2], bins=500, histtype='step', color='r', label= "Prompt with alpha")
plt.xlabel("Gamma energy (keV)")
plt.ylabel("Counts per 3 keV")
plt.legend(loc='best')
plt.show()
plt.clf()

# Gating on gamma energy
time_cut			= coincidence[(coincidence[:,4] >= 0) & (coincidence[:,4] <= coinc_window)]
all_alphas			= time_cut[(time_cut[:,1] == 1)]
coinc_with_gamma	= all_alphas[(all_alphas[:,2] >= gamma_gate_lower) & (all_alphas[:,2] <= gamma_gate_upper) & (all_alphas[:,3] == 0)]
prompt_coincs		= coinc_with_gamma[(coinc_with_gamma[:,4] >= t_start) & (coinc_with_gamma[:,4] <= t_finish)]
print "Alphas in prompt coinc with gammas: %i [%.f < Ea < %.f]" % (len(prompt_coincs), gamma_gate_lower, gamma_gate_upper)
#plt.hist(all_alphas[:,0], bins=500, histtype='stepfilled', color='b', label= "All alphas")
plt.hist(coinc_with_gamma[:,0], bins=250, histtype='step', color='b', label= "Coinc with gamma")
plt.hist(prompt_coincs[:,0], bins=250, histtype='step', color='r', label= "Prompt with gamma")
plt.xlabel("Alpha energy (keV)")
plt.ylabel("Counts per 12 keV")
plt.legend(loc='upper left')
plt.ylim(0, 25)
plt.show()
plt.clf()
### Alpha-gamma coincidences
# Gating on prompt coincidences																					# Alpha	channel			# Gamma channel
alpha_gamma_coinc	= coincidence[(coincidence[:,4] >= t_start) & (coincidence[:,4] <= t_finish) & (coincidence[:,1] == 1) & (coincidence[:,3] == 0)]
print "Prompt alpha-gamma coincs: %i [%.f < Ea < %.f] [%.f < Eg < %.f] [%.f < dt < %.f]" %( len(alpha_gamma_coinc), alpha_gate_lower, alpha_gate_upper, gamma_gate_lower, gamma_gate_upper, t_start, t_finish)
# Estimate the 2D histogram
H, xedges, yedges = np.histogram2d(alpha_gamma_coinc[:,2], alpha_gamma_coinc[:,0], [500, 500])
H = np.rot90(H)
H = np.flipud(H)
Hmasked = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero

# Plot 2D histogram using pcolor
plt.figure()
plt.pcolormesh(xedges,yedges,Hmasked)
plt.xlabel("Gamma energy (keV)")
plt.ylabel("Alpha energy (keV)")
plt.colorbar()
plt.title("Prompt alpha-gamma coincidences")
plt.ylim(5000, 5900)
plt.xlim(0, 400)
plt.show()
plt.clf()

alpha_gamma_coinc_all 	= coincidence[(coincidence[:,0] >= alpha_gate_lower) & (coincidence[:,0] <= alpha_gate_upper) & (coincidence[:,2] >= gamma_gate_lower) & (coincidence[:,2] <= gamma_gate_upper)]

# Plot histogram of time_delta
plt.hist(alpha_gamma_coinc_all[:,4], bins=10000, histtype='step', color='b')
plt.xlabel("Time between alpha-gamma events")
plt.ylabel("Counts")
plt.show()
plt.clf()
### Gamma-gamma coincidences
# Gating on delayed coincidences																	# Gamma channel				# Gamma channel
gamma_gamma_coinc	= coincidence[(coincidence[:,4] >= 255) & (coincidence[:,4] <= 265) & (coincidence[:,1] == 0) & (coincidence[:,3] == 0)]
gamma_gamma_coinc	= gamma_gamma_coinc[(gamma_gamma_coinc[:,0] >= 1400) & (gamma_gamma_coinc[:,0] <= 1600)]
gamma_gamma_coinc	= gamma_gamma_coinc[(gamma_gamma_coinc[:,2] >= 50) & (gamma_gamma_coinc[:,2] <= 150)]
print "Delayed gamma-gamma coincs: %i [%.f < Eg < %.f] [%.f < Eg < %.f] [%.f < dt < %.f]" %( len(gamma_gamma_coinc), 1400, 1600, 50, 250, 255, 265)

# Estimate the 2D histogram
H, xedges, yedges = np.histogram2d(gamma_gamma_coinc[:,2], gamma_gamma_coinc[:,0], [10, 30])
# H needs to be rotated and flipped
H = np.rot90(H)
H = np.flipud(H)
# Mask zeros
Hmasked = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
# Plot 2D histogram using pcolor
plt.figure()
plt.pcolormesh(xedges,yedges,Hmasked)
plt.xlabel("Gamma (CH2) energy (keV)")
plt.ylabel("Gamma (CH0) energy (keV)")
plt.colorbar()
plt.title("Delayed gamma-gamma coincidences")
plt.show()
plt.clf()
# Gating on gamma energy
time_cut			= coincidence[(coincidence[:,4] >= 255) & (coincidence[:,4] <= 265) & (coincidence[:,1] == 0)]
coinc_with_gamma1	= time_cut[(time_cut[:,2] >= 140) & (time_cut[:,2] <= 144) & (time_cut[:,3] == 0)]
print "Gammas in prompt coinc with gammas: %i [%.f < Eg < %.f]" % (len(coinc_with_gamma1), 140, 144)

plt.hist(time_cut[:,0], bins=np.arange(0,1500,2), histtype='step', color='b', label= "All gammas")
plt.hist(coinc_with_gamma1[:,0], bins=np.arange(0,1500,2), histtype='step', color='r', label= "Coinc with 142 keV gamma")
plt.xlabel("Gamma energy (keV)")
plt.ylabel("Counts")
plt.legend(loc='upper left')
plt.show()
plt.clf()

time_cut			= coincidence[(coincidence[:,4] >= 255) & (coincidence[:,4] <= 265) & (coincidence[:,3] == 0)]
coinc_with_gamma2	= time_cut[(time_cut[:,0] >= 1440) & (time_cut[:,0] <= 1460) & (time_cut[:,1] == 0)]
print "Gammas in prompt coinc with gammas: %i [%.f < Eg < %.f]" % (len(coinc_with_gamma2), 1440, 1460)
plt.hist(time_cut[:,2], bins=np.arange(0,1500,2), histtype='step', color='b', label= "All gammas")
plt.hist(coinc_with_gamma2[:,2], bins=np.arange(0,1500,2), histtype='step', color='r', label= "Coinc with 1450 keV gamma")
plt.xlabel("Gamma energy (keV)")
plt.ylabel("Counts")
plt.legend(loc='upper right')
plt.show()
plt.clf()
print "___________________________________________\n"
print "Time taken: ", (datetime.now()-startTime)
print "___________________________________________"
