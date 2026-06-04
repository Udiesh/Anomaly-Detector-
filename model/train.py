from sklearn.ensemble import IsolationForest
import joblib
import numpy as np

def generate_training_data():
    # normal transactions
    normal_amounts = np.random.uniform(10, 500, 900)
    normal_hours = np.random.randint(0, 24, 900)
    
    # anomalous transactions
    anomaly_amounts = np.random.uniform(5000, 20000, 100)
    anomaly_hours = np.random.randint(0, 24, 100)
    
    amounts = np.concatenate([normal_amounts, anomaly_amounts])
    hours = np.concatenate([normal_hours, anomaly_hours])
    return np.column_stack([amounts, hours])

def train():

    data = generate_training_data()
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(data)
    joblib.dump(model, "model/anomaly_model.pkl")
    print("Model trained and saved")

if __name__ == "__main__":
    train()