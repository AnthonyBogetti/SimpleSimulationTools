import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess

with open("cpptraj.in", "w") as file:
    file.write("parm ../common_files/4ake.prmtop"+"\n")
    file.write("trajin meld.nc.300K"+"\n")
    file.write("autoimage"+"\n")
    file.write("angle nmp-core :115-125 :90-100 :35-55 out disang.dat"+"\n")
    file.write("angle lid-core :179-185 :115-125 :125-153 out disang.dat"+"\n")

subprocess.run(['cpptraj', '-i', 'cpptraj.in'])

plt.rcParams.update({'font.size': 16, 'axes.linewidth': 1.5})

X = np.loadtxt("disang.dat", skiprows=1, usecols=1)
Y = np.loadtxt("disang.dat", skiprows=1, usecols=2)

xrange = np.arange(40,107,2)
yrange = np.arange(90,167,2)

fig, ax = plt.subplots(1, 1, figsize=(5,5))
hist, x_edges, y_edges = np.histogram2d(X, Y, bins=[xrange,yrange])

hist = np.transpose(hist)
hist = -np.log(hist / np.max(hist))

midpoints_x = (x_edges[:-1] + x_edges[1:]) / 2
midpoints_y = (y_edges[:-1] + y_edges[1:]) / 2

heatmap = ax.pcolormesh(midpoints_x, midpoints_y, hist, cmap="viridis", vmin=0, vmax=5)

# adjust plot
ax.set_xlim(40,105)
ax.set_ylim(90,165)
ax.set_xlabel("nmp-core angle")
ax.set_ylabel("lid-core angle")

# add colorbar and save the figure
fig.colorbar(heatmap, ax=ax, label="-ln(P)")
plt.tight_layout()
plt.show()
#plt.savefig("new_md_ff14sb.pdf")

os.remove("cpptraj.in")
os.remove("disang.dat")
