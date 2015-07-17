# vdrparser

*vdrparser* automatically extracts object--object relationships from images paired with descriptions. The instances that are automatically extracted can be used to train a model for predicting object--object relationships in new images. Ultimately, if you are interesting in generating text from these representations, you will want to get the [vdrDescription](https://github.com/elliottd/vdrDescription) package.

Dependencies
===

`vdrparser` inherits many dependencies from `MSTParser` and adds in a few of its own:

* Java 1.7+
* Apache Ant
* Python 2.7+ (Not Python 3, yet)
* Numpy
* Matplotlib
* Pandas
* Shapely
* NLTK 3.0
* stanford-postagger-full-2012-01-06 with `english-bidirectional-distsim.tagger`
* maltparser-1.7.2 with `engmalt.poly-1.7.mco`

If you are interested in language generation, you will also need to download [vdrDescription]
(https://github.com/elliottd/vdrDescription) and place in it in this
directory, and satisfy its dependencies.

Assumptions
===

The data is stored in the following manner in the `vdrparser` directory:

* data
  * [vlt2k](https://github.com/elliottd/vlt)
    * images (the JPG image files and HDF5 detection candidates from Caffe)
    * descriptions (the raw -{1,2,3}.desc files)

Extracting Object Proposals
===

You need to extract object proposals for all the images in the data set. We used the [Regions-with Convolutional Neural Network Features object detector](http://nbviewer.ipython.org/github/BVLC/caffe/blob/master/examples/detection.ipynb) in Caffe. We did this on a Tesla K20x GPU and recommend you also do it on a CUDA-compatible card. The resulting HDF5 files are approximately 7GB.

Run `python PrepareImages.py --path data/vlt2k/images/` to extract an individual HDF5 file to each image from the bactched output of the R-CNN detector.

Extracting Inferred VDR
===

Run `python selfTrain.py --images data/vlt2k/images --descriptions data/vlt2k/descriptions --vlt --verbose` to automatically extract inferred Visual Dependency Representations from the training dataset. This will POS Tag and Dependency Parse each sentence, then search for the referenced objects in the R-CNN proposals for each image.

If you keep the --verbose option, you can see the object--object detections and their relationships in the data/vlt2k/images/$X-objects.pdf files. This can be useful for diagnosing the effects of different types of extraction policies.

Optimising the VDR Parser
===

You need to train and optimise the VDR Parser so it has a good chance of predicting the important object--object relationships in images. The parsing model itself is still entirely based on the feature set from the COLING '14 paper [1]. What we'll want to do is optimise the number of objects extracted from an unseen image. (The objects detected with the highest confidence are not always the objects you need to best describe the image.)

You can optimise this parameter in the context of automatic image description. Run `python selfOptimise.py --images data/vlt2k/images --descriptions data/vlt2k/descriptions --maxobjects 20 --vlt --verbose` to find the best value for the number of objects to extract. We found that nine objects gives optimal Meteor scores in the development data.

Predicting Object--Object Relationships in Unseen Images
===

You will have already determined which value of `maxobjects` is best-suited to your dataset.

Run `python selfPredict.py --images data/vlt2k/images --descriptions data/vlt2k/descriptions --numbobjects 9 --vlt --test` to extract nine objects from each image in the test data, VDR Parse those objects into a (hopefully) useful object--object relationship structure, and then generate descriptions.

Questions, comments, etc.
===

elliott@cwi.nl or [delliott](http://www.twitter.com/delliott)

(I came here looking for the old gold-standard code)
---

You will want to grab the code in the [goldStandardAnnotations](https://github.com/elliottd/vdrparser/tree/goldStandardAnnotations) branch.
