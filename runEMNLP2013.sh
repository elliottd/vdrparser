#!/bin/sh

# Train the VDR Parsing Model. No visual features for the EMNLP paper.
python trainVDRParser.py --path data/vlt/emnlp2013/ --model mst -k 5 --decoder non-proj --split true --runString VDR

# Predict the VDRs for the test splits.
python testVDRParser.py -p data/vlt/emnlp2013/ --model mst -k 5 --decoder non-proj --split true --runString VDR 

# Evaluate the performance of the EMNLP VDR Parsing Model
python evaluateVDRParser.py --path data/vlt/emnlp2013/ --model mst -k 5 --decoder non-proj --split true --runString VDR 
