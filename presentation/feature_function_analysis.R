aaa <- read.csv("processed", header=TRUE)
pdf("sd")
library(ggplot2)


count_group <- data.frame(user=factor(rep(1:50, 2)), 
                          count=sample(100, 100, replace=T), 
                          group=factor(rep(LETTERS[1:20], 5)))

library(RColorBrewer)
cols <- colorRampPalette(brewer.pal(9, "Set1"))
ngroups <- length(unique(data$type))
qplot(aaa$weight, aaa$type, geom="bar")
dev.off()

library(ggplot2)
pdf("sd")
aaa <- read.csv("processed", header=TRUE)
aaa$type<-as.factor(aaa$type)
par(mfrow=c(2,2))
ggplot(aaa, aes(x=c(1:nrow(aaa)), y=aaa$weight, fill=aaa$type)) + geom_bar(stat="identity") + scale_fill_manual(values=c("#CC6666", "#FFFFFF", "#FFFFFF", "#FFFFFF","#FFFFFF","#FFFFFF"))
ggplot(aaa, aes(x=c(1:nrow(aaa)), y=aaa$weight, fill=aaa$type)) + geom_bar(stat="identity") + scale_fill_manual(values=c("#FFFFFF","#CC6666", "#FFFFFF", "#FFFFFF","#FFFFFF","#FFFFFF"))
ggplot(aaa, aes(x=c(1:nrow(aaa)), y=aaa$weight, fill=aaa$type)) + geom_bar(stat="identity") + scale_fill_manual(values=c("#FFFFFF","#FFFFFF", "#CC6666", "#FFFFFF","#FFFFFF","#FFFFFF"))
ggplot(aaa, aes(x=c(1:nrow(aaa)), y=aaa$weight, fill=aaa$type)) + geom_bar(stat="identity") + scale_fill_manual(values=c("#FFFFFF", "#FFFFFF", "#FFFFFF","#CC6666","#FFFFFF","#FFFFFF"))
dev.off()

