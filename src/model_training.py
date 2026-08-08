import pandas as pd
import numpy as np
import os

import pickle

from sklearn.ensemble import RandomForestClassifier

# Read the training dataset
train_data = pd.read_csv("./data/processed/train_processed.csv")

# Split features and target
X_train = train_data.iloc[:, 0:-1].values
y_train = train_data.iloc[:, -1].values

# Train the model
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Save the trained model
pickle.dump(clf, open("model.pkl", "wb"))