#load
library(GD)
library(readxl)

options(scipen=200) ##It means that scientific counting is not used within 200 numbers.
#Read data
data<-read_excel("./urbanData_GeoDetector.xls",sheet="Sheet1")
#Grading method
discmethod <- c("natural","quantile","geometric","sd")#Optional classification methods include "equal","natural","quantile","geometric","sd" . 

#Number of grades
discitv <- c(3:6)
#******Data re-edit, check
data2<-edit(data)

#Main function
transform<-gdm(Y~X1+X2+X3+X4+X5+X6+X7,
               continuous_variable=c("X1","X2","X3","X4","X5","X6","X7"),
               data=data2,
               discmethod=discmethod,
               discitv=discitv)
transform

