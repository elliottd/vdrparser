VDRParser
---------

VDRParser is a fork of the MSTParser [1] to predict Visual Dependency
Representations of images. Visual Dependency Representations capture the
spatial relationships between objects in an image and have been used for image
description [2] and example-based image search [3]. Further details on the
representation can also be found on the data set page
http://homepages.inf.ed.ac.uk/s0128959/dataset/

Dependencies
------------

The VDRParser depends on the following libraries.

 * apache ant
 * python-rpy2
 * python2.7
 * java7
 * python-numpy

Usage
-----

You can train the VDRParser using the following command:

`python trainVDRParser.py --path {path to split data} --model mst -k 5 --decoder non-proj --split true`

Use a trained VDRParser model to predict VDRs on test data:

`python testVDRParser.py --path {path to split data} --model mst -k 5 --decoder non-proj --split true`

And evaluate the accuracy of the parsing model:

`python evaluateVDRParser.py --path {path to split data} --model mst -k 5 --decoder non-proj --split true`

EMNLP 2013 Results
--------------

The EMNLP 2013 VDRParser [2] only extracts features from the CoNLL-X formatted
representation. To reproduce the EMNLP 2013 results, download the [Visual and
Linguistic Treebank Dataset](http://homepages.inf.ed.ac.uk/s0128959/dataset/) and extract into
`data/vlt/emnlp2013`

Run `./runEMNLP2013.sh` to train, predict, and evaluate this parsing model. By
default, we evaluate on the `dev` data, but you can run on the `test` data by 
adding the argument `--test true` in the `testVDR` and `evalauteVDR` commands. 

You should expect to see the following results:

|                | Dev         | Test        |
| -------------  | ---------   | ----------- |
| **Labelled**   |             |             |
| Mean Directed  | 53.7 +- 3.5 | 54.0 +- 4.7 |
| Mean Root      | 87.4 +- 3.2 | 87.9 +- 4.2 |
| Mean Dep       | 21.3 +- 4.3 | 21.7 +- 4.3 |
|                |             |             |
| Mean F1        | 60.0 +- 2.7 | 58.4 +- 3.4 |
| Mean P         | 58.5 +- 2.8 | 61.1 +- 2.9 |
| Mean R         | 60.0 +- 2.7 | 56.8 +- 3.7 |
|                |             |             |
| **Unlabelled** |             |             |
| Mean Directed  | 62.4 +- 3.2 | 62.0 +- 4.8 |
| Mean Root      | 87.3 +- 3.2 | 87.9 +- 4.2 |
| Mean Dep       | 38.4 +- 4.7 | 37.2 +- 5.8 |


COLING 2014 Results
---------------

The COLING2014 VDRParser [3] also extracts features from the image regions to
improve the parsing results.  representation. To reproduce the EMNLP 2013
results, download the [Visual and
Linguistic Treebank Dataset](http://homepages.inf.ed.ac.uk/s0128959/dataset/) and extract into `data/emnlp2013`

You need to run modify the absolute paths to the image files using
`updateAnnotationLocations.sh` in the `data/vlt/emnlp2013` directory before
continuing or the parser will not work.

Run `./runCOLING2014.sh` to train, predict, and evaluate this parsing model. By
default, we evaluate on the `dev` data, but you can run on the `test` data by 
adding the argument `--test true` in the `testVDR` and `evalauteVDR` commands. 

You should expect to see the following results:

|                | Dev         | Test        |
| -------------  | ---------   | ----------- |
| **Labelled**   |             |             |
| Mean Directed  | 54.5 +- 2.6 | 55.2 +- 5.0 |
| Mean Root      | 88.9 +- 3.1 | 89.3 +- 2.6 |
| Mean Dep       | 21.2 +- 3.4 | 22.6 +- 4.9 |
|                |             |             |
| Mean F1        | 60.1 +- 1.7 | 59.8 +- 3.5 |
| Mean P         | 62.1 +- 1.8 | 61.8 +- 3.2 |
| Mean R         | 59.0 +- 1.8 | 58.6 +- 3.7 |
|                |             |             |
| **Unlabelled** |             |             |
| Mean Directed  | 63.4 +- 3.0 | 64.1 +- 5.1 |
| Mean Root      | 88.9 +- 3.1 | 89.3 +- 2.6 |
| Mean Dep       | 38.9 +- 4.5 | 40.2 +- 6.5 |

References
----------

[1] R. McDonald, F. Pereira, K. Ribarov and J. Hajič. 2005. Non-Projective
Dependency Parsing using Spanning Tree Algorithms. Human Language Technologies
and Empirical Methods in Natural Language Processing (HLT-EMNLP), Vancouver,
British Columbia, Canada.

[2] D. Elliott and F. Keller. 2013. Image Description using Visual Dependency
Representations. In Proceedings of the 2013 Conference on Empirical Methods in
Natural Language Processing (EMNLP '13), Seattle, Washington, U.S.A

[3] D. Elliott, V. Lavrenko, and F. Keller. 2014. Query-by-Example Image
Retrieval using Visual Dependency Representations. In Proceedings of the 25th
International Conference on Computational Linguistics (COLING '14), Dublin,
Ireland.

Contact
-------
elliott@cwi.nl

or

@delliott

