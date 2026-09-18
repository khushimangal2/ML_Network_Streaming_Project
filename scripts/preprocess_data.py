import pandas as pd

input_file = "../data/processed_network_data.csv"
output_file = "../data/cleaned_network_data.csv"
# Load the processed network data
df = pd.read_csv(input_file)

# Remove rows with missing values
df = df.dropna()

# Remove duplicate rows
df = df.drop_duplicates()

# Save cleaned data
df.to_csv(output_file, index=False)

print("Data preprocessing completed successfully!")
print("Cleaned data saved to:", output_file)
