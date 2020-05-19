import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

data = pd.read_csv("training_data/training_data.csv")

mymap = {'':0, 'A':1, 'B':2, 'C':3, 'D':4, 'E':5}

tgt = data['target']
train1 = data.applymap(lambda s: mymap.get(s) if s in mymap else s).drop(['target',],axis=1)

values = {'f1': 0, 'f2': 0, 'f3': 0}
train1 = train1.fillna(value=values)

col_imp = ["f1", "f2", "f3"]

clf = GradientBoostingRegressor(n_estimators = 400, max_depth = 5, min_samples_split = 2)
clf.fit(train1[col_imp], tgt)

def predict(f1, f2, f3, clf=clf):
    try:
        f3_rep = f3.replace('','0').replace('A','1').replace('B','2').replace('C','3').replace('D','4').replace('E','5')
        f3_int = int(f3_rep)
    except:
        f3_int = 0
    x = np.array([[f1,f2,f3_int]])
    y_pred = clf.predict(x)[0]
    return round(y_pred)
