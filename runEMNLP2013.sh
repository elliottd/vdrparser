#!/bin/sh

# Train the VDR Parsing Model. No visual features for the EMNLP paper.
python trainVDRParser.py -p data/tmp/ -m mst -k 5 -d non-proj -s 10 -f true

# Predict the VDRs for the test splits.
python testVDRParser.py -p data/tmp/ -m mst -k 5 -d non-proj -s 10 -f true

# Evaluate the performance of the EMNLP VDR Parsing Model
python evaluateVDRParser.py -p data/tmp/ -s 10 -f true
