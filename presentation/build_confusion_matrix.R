# Your model output file should be in the format
# Ground Truth,Prediction
#             .
#             .

library("ggplot2")

# your model output file is the command line argument
args <- commandArgs(trailingOnly=TRUE)
# you might want to change the separator if your data is already on disk
data<-read.csv(args, sep=",") 
names(data) <- c("Actual","Predicted")
actual <- as.data.frame(table(data$Actual))
names(actual) <- c("Actual","ActualFreq")

#construct confusion matrix
confusion <- as.data.frame(table(data$Actual, data$Predicted))
names(confusion) <- c("Actual","Predicted","Freq")

#calculate percentage of test cases based on actual frequency
confusion <- merge(confusion, actual, by=c("Actual"))
confusion$Percent <- confusion$Freq / confusion$ActualFreq*100

# prepare the plot in an virtual buffer
tile <- ggplot() + geom_tile(aes(x=Actual, y=Predicted, fill=Percent), data=confusion, color="black", size=0.1) + labs(x="Actual", y="Predicted") + scale_fill_gradient(low="white", high="black") + opts(legend.position = 'bottom')

# draw the plot to disk
pdf(file="confusion_matrix.pdf")
tile
dev.off()
