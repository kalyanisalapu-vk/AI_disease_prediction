import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load training dataset
data = pd.read_csv("Training.csv")

# Remove unnecessary empty column
data = data.drop(columns=["Unnamed: 133"])

# Separate symptoms and disease
X = data.drop(columns=["prognosis"])
y = data["prognosis"]

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Create the model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

# Test the model
predictions = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, predictions)

print("Model Accuracy:", accuracy)
# Save the trained model
joblib.dump(model, "disease_model.pkl")

# Save symptom column names
joblib.dump(X.columns.tolist(), "symptoms.pkl")

print("\nModel saved successfully!")
print("Symptoms saved successfully!")