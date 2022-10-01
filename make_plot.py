import datetime

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

import pandas as pd

# read data
by_month = pd.read_parquet("results.parquet").groupby("date").has_matplotlib.mean()


# get figure
fig, ax = plt.subplots(layout="constrained")
# plot the data
ax.plot(by_month, "o", color="k", ms=3)

# over-ride the default auto limits
ax.set_xlim(left=datetime.date(2004, 1, 1))
ax.set_ylim(bottom=0)

# turn on a horizontal grid
ax.grid(axis="y")

# remove the top and right spines
ax.spines.right.set_visible(False)
ax.spines.top.set_visible(False)

# format y-ticks a percent
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))

# add title and labels
ax.set_xlabel("date")
ax.set_ylabel("% of all papers")
ax.set_title("Matplotlib usage on arXiv")

fig.savefig("fancy_plot.png")
