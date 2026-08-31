from pathlib import Path
import pickle

import pandas as pd
from fastapi import FastAPI

try:
    from src.data_model import Water
except ImportError:  # pragma: no cover - supports running the module directly
    from data_model import Water

app = FastAPI(
    title="Water Potability Prediction",
    description="Predicting Water Potability",
)
 # Setting path for model.pkl file and loading the model
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model.pkl"

with MODEL_PATH.open("rb") as f:
    model = pickle.load(f)


@app.get("/")
def index():
    return {"message": "Welcome to Water Potability Prediction FastAPI"}


@app.post("/predict")
def model_predict(payload: Water):
    sample = pd.DataFrame(
        [{
            "ph": payload.ph,
            "Hardness": payload.Hardness,
            "Solids": payload.Solids,
            "Chloramines": payload.Chloramines,
            "Sulfate": payload.Sulfate,
            "Conductivity": payload.Conductivity,
            "Organic_carbon": payload.Organic_carbon,
            "Trihalomethanes": payload.Trihalomethanes,
            "Turbidity": payload.Turbidity,
        }]
    )

    predicted_value = int(model.predict(sample)[0])
    prediction = "Water is Consumable" if predicted_value == 1 else "Water is not Consumable"
    return {"prediction": prediction}
