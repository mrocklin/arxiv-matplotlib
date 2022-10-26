# arXiv Matplotlib Query

Anecdotally the Matplotlib maintainers were told

*"About 15% of arXiv papers use Matplotlib"*

Unfortunately the original analysis of this data was lost.  We reproduce it here.

## Watermark

Starting in the early 2010s, Matplotlib started including the bytes `b"Matplotlib"` in every PNG and PDF that they produce.  These bytes persist in the output PDFs stored on arXiv.  As a result, it's pretty simple to check if a PDF contains a Matplotlib image.  All we have to do is scan through every PDF and look for these bytes; no parsing required.

## Data

The data is stored in a requester pays bucket at s3://arxiv (more information at https://arxiv.org/help/bulk_data_s3 ) and also on GCS hosted by Kaggle (more information at https://www.kaggle.com/datasets/Cornell-University/arxiv).

The data is about 1TB in size.  We use Dask for this.

## Contents

This repository has the notebook used to generate the data,
the data itself as a parquet file,
and a nice image showing growing usage.


## Results

![A plot of Matplotlib usage on arVix showing strong growth from 2004 to 2022 from 0 to 17%](results.png?raw=true "Matplotlib usage on arXiv over time")
