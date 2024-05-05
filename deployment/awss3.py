import pickle

prec = pickle.load(open('https://timeseriesmodel.s3.amazonaws.com/preprocessor.prec', 'rb'))

print(prec)