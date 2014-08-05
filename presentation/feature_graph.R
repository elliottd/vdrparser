mydata <- read.table("output/results.csv", header=TRUE, sep=",")
pdf(file="features.pdf")
par(mar=c(3,3,8,3), xpd=TRUE)
barplot(t(mydata[-1]), beside=T, names.arg=mydata$id, col=rainbow(7), ylab="Accuracy", xlab="Feature set", xpd=FALSE, ylim=c(30,90))
legend("topleft", fill=rainbow(7), horiz=T, legend=rownames(t(mydata[-1])), inset=c(0,-0.1))
dev.off()

