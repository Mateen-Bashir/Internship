from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import xgboost as xgb
import os

app = FastAPI(title="Intern Performance Prediction API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's a local dev project
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models
try:
    imputer = joblib.load("imputer.pkl")
    rf_model = joblib.load("random_forest_model.pkl")
    xgb_model = xgb.XGBRegressor()
    xgb_model.load_model("xgboost_model.json")
except Exception as e:
    print(f"Error loading models. Have they been generated via train_model.py? Details: {e}")

class InternData(BaseModel):
    Completion_Time: float
    Feedback_Rating: float
    Attendance: float

@app.get("/")
def read_root():
    return {"message": "Welcome to Intern Performance Prediction API"}

@app.post("/predict")
def predict(data: InternData):
    try:
        # Create a DataFrame for the scaler
        df_input = pd.DataFrame([{
            'Completion_Time': data.Completion_Time,
            'Feedback_Rating': data.Feedback_Rating,
            'Attendance': data.Attendance
        }])
        
        # Impute missing scales as per training
        X_imputed = imputer.transform(df_input)

        # We'll use XGBoost as the primary model due to marginally better performance
        # but you can easily switch or combine
        xgb_prediction = xgb_model.predict(X_imputed)[0]
        rf_prediction = rf_model.predict(X_imputed)[0]

        return {
            "prediction": float(xgb_prediction),
            "rf_prediction_reference": float(rf_prediction)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
