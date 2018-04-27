#!/usr/bin/env python

import matplotlib.pyplot as plt
from numpy import arange,sqrt
# fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
# inches_per_pt = 1.0/72.27               # Convert pt to inch
# golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
# fig_width = fig_width_pt*inches_per_pt  # width in inches
# fig_height = fig_width*golden_mean      # height in inches
# fig_size =  [fig_width,fig_height]
# params = {'backend': 'ps',
#           'axes.labelsize': 10,
#           'text.fontsize': 10,
#           'legend.fontsize': 10,
#           'xtick.labelsize': 8,
#           'ytick.labelsize': 8,
#           'text.usetex': True,
#           'figure.figsize': fig_size}
# pylab.rcParams.update(params)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

def MCMC_plot(all_scores, eps, burn_in, name):
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    # Need all them to run the same amount
    x = len(all_scores[0])

    plt.figure(1)
    plt.clf()
    for i,scores in enumerate(all_scores):
        # Get the faux points to have graph start from 0 (as opposed to burn_in)
        # PROBABLY A BETTER WAY TO DO THIS
        # burn_in_slope = scores[0]/burn_in
        points_from_zero = []
        # for j in range(burn_in):
        #     points_from_zero.append(j*burn_in_slope)
        points_from_zero += scores
        if eps[i] == '_':
            plt.plot(range(x),points_from_zero,color=colors[i],label='orig')
        else:
            plt.plot(range(x),points_from_zero,color=colors[i],label='ep' + str(eps[i]))
    plt.xlabel('step')
    plt.ylabel('log$(L*P)$')
    plt.legend()

    plt.savefig(name)
