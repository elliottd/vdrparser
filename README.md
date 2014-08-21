VDRParser
---------


###Dependencies:

    apache ant
    python-rpy2

###Usage

You can train the VDRParser using the following command:

> python trainVDRParser.py -p data/emnlp2013/ -m mst -k 5 -d non-proj -s 10 -f true

Use a trained VDRParser model to predict VDRs on test data:

> python testVDRParser.py -p data/emnlp2013/ -m mst -k 5 -d non-proj -s 10 -f true

And evaluate the accuracy of the parsing model:

> python evaluateVDRParser.py -p data/emnlp2013/ -s 10 -f true

EMNLP 2013
----------

The EMNLP 2013 VDRParser only extracts features from the CoNLL-X formatted representation. To reproduce the EMNLP 2013 results, ./runEMNLP2013.sh

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

COLING 2014
-----------

The COLING2014 VDRParser [2] also extracts features from the image regions to improve the parsing results. To reproduce these results, ./runCOLING2014.sh

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
    
References
----------

[1] D. Elliott and F. Keller. 2013. Image Description using Visual Dependency Representations. In Proceedings of the 2013 Conference on Empirical Methods in Natural Language Processing (EMNLP '13), Seattle, Washington, U.S.A

[2] D. Elliott, V. Lavrenko, and F. Keller. 2014. Query-by-Example Image Retrieval using Visual Dependency Representations. In Proceedings of the 25th International Conference on Computational Linguistics (COLING '14), Dublin, Ireland.
