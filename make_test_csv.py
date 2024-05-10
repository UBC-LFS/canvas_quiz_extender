import pandas as pd

# Original data
data = {
    "Student": ["John Smith", "Demi Demo", "Zoe Zemo"],
    "Extension": [1.5, 2.0, 4.0, 5.0],
    "Quizzes": [721805, 1801136],
}

# Determine the maximum list length
max_length = max(len(lst) for lst in data.values())

# Create a list of dictionaries, each representing a row in the DataFrame
rows = []
for i in range(max_length):
    row = {key: data[key][i] if i < len(data[key]) else None for key in data}
    rows.append(row)

# Create the DataFrame
df = pd.DataFrame(rows)

# Specify your CSV file name
file_name = "extensions.csv"

# Write the DataFrame to a CSV file
df.to_csv(file_name, index=False)

print(f"CSV file '{file_name}' created successfully.")
