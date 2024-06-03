import datetime
from functools import lru_cache
import time
import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib as mpl

import numpy as np
import pandas as pd

import requests
import feedparser
import tqdm

mpl.rcParams["date.autoformatter.year"] = "'%y"

# read data
raw_data = pd.read_parquet("results.parquet")
Path("cache").mkdir(exist_ok=True)


@lru_cache(10240)
def get(url):
    # wrap requests.get in caching + rate limiting
    fn = hashlib.md5(url.encode()).hexdigest()
    cache_path = Path("cache") / fn
    if cache_path.exists():
        with open(cache_path) as fin:
            return fin.read()

    ret = requests.get(url)
    with open(cache_path, "w") as fout:
        fout.write(ret.text)

    # arxiv as a on-your-honor rate limit at 1 per 3s (!!)
    time.sleep(3)
    return ret.text


def entry_to_id(entry):
    """Convert id in entry into id extracted from pdf filenames."""
    if not entry["guidislink"]:
        raise ValueError
    arxivid, v, _ = entry["id"][21:].partition("v")
    return arxivid


res = {}
# this is very long (10hr+) the first time it is run, the caching helps
for month in tqdm.tqdm(
    [f"20{year:02d}-{month:02d}-01" for year in range(8, 25) for month in range(1, 13)]
):
    print(month)
    # in 2009 astro-ph was split into 6 sub-categories
    if month < "2009-01":
        cats = "cat:astro-ph"
    else:
        cats = "+OR+".join(
            f"cat:astro-ph.{sc}" for sc in "GA,CO,EP,HE,IM,SR".split(",")
        )
    parsed = []
    one_month = raw_data[raw_data["date"] == month]
    if not len(one_month):
        continue
    one_month.insert(0, "arxiv_id", one_month["filename"].str[5:-4])
    # do in 150 paper chunks to stay below maximum URL length
    for j in tqdm.tqdm(range(0, len(one_month), 150)):
        ids = ",".join(one_month["arxiv_id"][j : j + 150])
        url = f"http://export.arxiv.org/api/query?search_query={cats}&id_list={ids}&max_results=150"
        parsed.append(feedparser.parse(get(url)))
    # make a 1 column DataFrame to merge with the raw data to select only the astro papers.
    # probably exists a better way.
    astroph = pd.DataFrame(
        {"arxiv_id": [entry_to_id(e) for b in parsed for e in b["entries"]]}
    )
    res[month] = one_month.merge(astroph, on="arxiv_id").has_matplotlib.mean()
    print(f"{month}: {res[month]}")

# make series of astro-ph papers by month
astro = pd.Series(list(res.values()), index=pd.to_datetime(list(res)))

# rmake series of astro-ph papers by month
by_month = raw_data.groupby("date").has_matplotlib.mean()

# size for half page figure on letter paper
# figsize = np.array([(8.5 - 2) * 0.45, 3])
figsize = None
# get figure
fig, ax = plt.subplots(layout="constrained", figsize=figsize)
# plot the data
ax.plot(astro, "s", color="k", ms=3, label="astro-ph")
ax.plot(by_month, "o", color=".7", ms=3, label="all")
# add a legend
ax.legend()

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
ax.set_ylabel("% of uploaded papers")
ax.set_title("Matplotlib usage on arXiv")

# output
fig.savefig("fancy_plot.png")
plt.show()


# this would seem to be a better path to get all the astro papers, but after
# ~3k entries stops returning contents in the payload.  think this is a
# limitation on the server side that they trim huge searches

# count = 0
# cat_search_parsed = []
# for j in tqdm.tqdm(range(5*12*20)):
#     url = f'http://export.arxiv.org/api/query?search_query={cats}&max_results=500&start={count}&sortBy=submittedDate&sortOrder=descending'
#     print(url)
#     feed = feedparser.parse(get(url))
#     cat_search_parsed.extend(feed['entries'])
#     count += len(feed['entries'])
#     if len(feed['entries']) == 0:
#         break
#
