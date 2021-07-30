import pickle

models = {}

with open('model\\apps15_new', 'rb') as input_file:
    models["New"] = pickle.load(input_file)

with open('model\\apps15_rep', 'rb') as input_file:
    models["Repeat"] = pickle.load(input_file)
    