import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import joblib

def main():
    print("Loading data...")
    # Load dataset
    data_path = "dataset/intern_dataset_realistic (1).csv"
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {data_path}")
        return

    print("Data loaded successfully. Basic Info:")
    print(df.info())

    # Drop ID column if exists
    if 'Intern_ID' in df.columns:
        df.drop('Intern_ID', axis=1, inplace=True)

    # Separate features and target
    X = df.drop('Performance_Score', axis=1)
    y = df['Performance_Score']

    # Handle missing values
    print("Handling missing values...")
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    
    # Save the imputer for future inferences
    joblib.dump(imputer, 'imputer.pkl')

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.2, random_state=42)
    print(f"Training data shape: {X_train.shape}, Testing data shape: {X_test.shape}")

    # Random Forest Model
    print("\nTraining Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_mse = mean_squared_error(y_test, rf_preds)
    rf_r2 = r2_score(y_test, rf_preds)
    print(f"Random Forest - MSE: {rf_mse:.4f}, R2 Score: {rf_r2:.4f}")

    # XGBoost Model
    print("\nTraining XGBoost Regressor...")
    xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror')
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_mse = mean_squared_error(y_test, xgb_preds)
    xgb_r2 = r2_score(y_test, xgb_preds)
    print(f"XGBoost - MSE: {xgb_mse:.4f}, R2 Score: {xgb_r2:.4f}")

    # Save Models
    print("\nSaving models...")
    joblib.dump(rf_model, 'random_forest_model.pkl')
    xgb_model.save_model('xgboost_model.json')
    print("Models saved successfully: 'random_forest_model.pkl' and 'xgboost_model.json'")

if __name__ == "__main__":
    main()
