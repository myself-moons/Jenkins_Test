import pandas as pd
import pickle
import json

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Load test dataset
test_data = pd.read_csv("./data/processed/test_processed.csv")

# Split features and target
X_test = test_data.iloc[:, :-1].values
y_test = test_data.iloc[:, -1].values

# Load trained model
model = pickle.load(open("model.pkl", "rb"))

# Make predictions
y_pred = model.predict(X_test)

# Calculate evaluation metrics
acc = accuracy_score(y_test, y_pred)
pre = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1score = f1_score(y_test, y_pred)

# Store metrics in a dictionary
metrics_dict = {
    "acc": acc,
    "precision": pre,
    "recall": recall,
    "f1_score": f1score
}

# Save metrics to a JSON file
with open("metrics.json", "w") as file:
    json.dump(metrics_dict, file, indent=4)