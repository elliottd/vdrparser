Dependencies:

  apache ant
  python-rpy2

python trainVDRParser.py -p data/emnlp2013/ -m mst -k 5 -d non-proj -s 10 -f true

python testVDRParser.py -p data/emnlp2013/ -m mst -k 5 -d non-proj -s 10 -f true

python evaluateVDRParser.py -p data/emnlp2013/ -s 10 -f true

To reproduced the EMNLP 2013 results, ./runEMNLP2013.sh

Labelled
Mean Directed: 54.033 +- 4.687
Mean Root: 87.861 +- 4.234
Mean Dep: 21.654 +- 4.311

Unlabelled
Mean Directed: 61.959 +- 4.765
Mean Root: 87.861 +- 4.234
Mean Dep: 37.217 +- 5.812

Mean Undirected: 76.541 +- 3.608

Mean F1: 58.433 +- 3.356
Mean P: 61.082 +- 2.887
Mean R: 56.844 +- 3.654

To reproduce the COLING 2014 VDR Parsing results, ./runCOLING2014.sh

Labelled
Mean Directed: 55.182 +- 4.963
Mean Root: 89.280 +- 2.625
Mean Dep: 22.616 +- 4.905

Unlabelled
Mean Directed: 64.120 +- 5.082
Mean Root: 89.280 +- 2.625
Mean Dep: 40.183 +- 6.538

Mean Undirected: 77.284 +- 4.171

Mean F1: 59.825 +- 3.464
Mean P: 61.842 +- 3.233
Mean R: 58.599 +- 3.694
