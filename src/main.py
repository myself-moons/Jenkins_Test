from fastapi import FastAPI
import pickle

app = FastAPI(
    title = "Water Potability Prediction API",
    description = "This API predicts the potability of water based on various features using a trained machine learning model.",
    version = "1.0.0"
)

with open("model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

@app.get("/")
def index():
    return {"message": "Welcome to the Water Potability Prediction API. Use the /predict endpoint to get predictions."}