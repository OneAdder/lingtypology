#Rips normal CSV out of RData

data = get(load('autotyp.RData'))
write.csv(data, file='autotyp.csv')
