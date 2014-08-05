
    if model == "mst" or "qdgmst":
        create_confusion_matrix(runname)

        handle = open(runname+"-dicts", "rb")
        labelled_root = pickle.load(handle)
        labelled_dep = pickle.load(handle)
        handle.close()
        ext = 'pdf'
        dev = {'eps' : (r.postscript, 'gv'), 'pdf' : (r.pdf, 'evince'), 'png' : (r.png, 'display'), 'fig' : (r.xfig, 'xfig')}
        fn= runname+"-root."+ ext
        dev[ext][0](fn)
        root_bars = numpy.array([[numpy.mean(x[1]) for x in sorted(labelled_root.items())]])
        root_se = numpy.array([[sem(x[1]) for x in sorted(labelled_root.items())]])
        dep_bars = numpy.array([[numpy.mean(x[1]) for x in sorted(labelled_dep.items())[1:]]])
        dep_se = numpy.array([[sem(x[1]) for x in sorted(labelled_dep.items())[1:]]])
        #r.par(mfrow=(2,1))
        r.plot((1,2,3,4,5,6,7,8,9,10), root_bars, ylab="Root Accuracy", type="n", xaxt="n", ylim=(0.5,1), xlab="")
        r.axis(1, at=range(1,11), labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"])
        r.lines((1,2,3,4,5,6,7,8,9,10), root_bars)
        r.arrows((1,2,3,4,5,6,7,8,9,10), root_bars - root_se, (1,2,3,4,5,6,7,8,9,10), root_bars + root_se, angle=90, length=0.1, code=3, lwd=1)
        r.dev_off()
        #os.system(dev[ext][1] + " " + fn)
        fn = runname+"-dep."+ext
        dev[ext][0](fn)
        r.plot((1,2,3,4,5,6,7,8,9), dep_bars, xlab="Number of image regions", ylab="Non-root Accuracy", type="n", xaxt="n", ylim=(0,0.5))
        r.axis(1, at=range(1,10), labels=["2", "3", "4", "5", "6", "7", "8", "9", "10+"])
        r.lines((1,2,3,4,5,6,7,8,9), dep_bars)
        r.arrows((1,2,3,4,5,6,7,8,9), dep_bars - dep_se, (1,2,3,4,5,6,7,8,9), dep_bars + dep_se, angle=90, length=0.1, code=3, lwd=1)
        r.dev_off()

