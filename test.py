verbosity = [] #["progress","mine","rule","sample","label"],
c = CorelsClassifier(verbosity=verbosity, c=0.00001)

nsamples = 1000
nfeatures = 6
x = np.random.randint(2, size=[nsamples, nfeatures], dtype=np.bool)
y = np.random.randint(2, size=nsamples, dtype=np.bool)

#x = np.array([ [1, 0, 1], [0, 1, 0], [1, 1, 1] ])
#y = np.array([ 1, 0, 1])

rl = c.fit(x, y, max_card=1)

print(rl.features)
print(rl.rules)
print(rl.ids)
print(rl)
