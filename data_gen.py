import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic data
num_samples = 5000
ages = np.random.randint(1, 100, num_samples)  # Age from 1 to 99
weights = np.random.randint(1, 100, num_samples)  # Weight from 30 to 100 kg
severity = np.random.uniform(0.1, 10.0, num_samples)  # Severity from 0.1 to 10.0 (float)
factor = np.random.choice([8, 9], num_samples)  # Factor 8 or 9

# Define priority: Small kids (age < 12) and old people (age > 60) have higher priority
priority = np.where(ages < 12, 1.0, np.where(ages > 60, 1.0, 2.0))
priority += np.where(factor == 8, -0.5, 0.0)  # Factor 8 adds more priority (lower value)
priority = priority - (severity / 10)  # Higher severity reduces priority

# Normalize and scale priority to range from 1 to num_samples
priority = (priority - priority.min()) / (priority.max() - priority.min()) * (num_samples - 1) + 1
priority = np.round(priority).astype(int)

# Create DataFrame
data = pd.DataFrame({
    'age': ages,
    'weight': weights,
    'severity': severity,
    'factor': factor,
    'priority': priority
})

# Show the first few rows of the dataset
print(data.head())

# Write the data to a CSV file
data.to_csv('hemophilia_patient_data.csv', index=False)
