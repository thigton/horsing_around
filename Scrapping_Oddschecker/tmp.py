import pickle
import numpy as np
import os
alpha = np.ones((50,50))*0.05
os.chdir(os.path.dirname(os.path.realpath(__file__))) 
with open('alpha.pickle','wb') as pickle_out:
    pickle.dump(alpha, pickle_out)