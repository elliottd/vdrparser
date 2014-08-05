python trainVDRParser.py -p data/emnlp2013/ -m mst -k 5 -d non-proj -s 10 -f true

python testVDRParser.py -p data/emnlp2013/ -m mst -k 5 -d non-proj -s 10 -f true

python evaluateVDRParser.py -p data/emnlp2013/ -s 10 -f true
