import pandas as pd
import os

# List of CSV file paths
csv_files = [
    "financial_terms_batch1.csv",
    "financial_terms_batch2.csv",
    "financial_terms_batch3.csv",
    "financial_terms_batch4.csv",
    "financial_terms_batch5.csv",
    "financial_terms_batch6.csv",
    "financial_terms_batch7.csv",
    "financial_terms_batch8.csv",
    "financial_terms_batch9.csv",
    "financial_terms_batch10.csv"
]

# Directory where the CSV files are located
directory = "FinancialTermsCSV's"

# List to hold dataframes
dataframes = []

# Read each CSV file and append to the list
for file in csv_files:
    df = pd.read_csv(os.path.join(directory, file))
    dataframes.append(df)

# Concatenate all dataframes
merged_df = pd.concat(dataframes, ignore_index=True)

# Remove duplicate terms
merged_df.drop_duplicates(subset="Term", keep="first", inplace=True)

# Save the merged dataframe to a new CSV file
merged_csv_file_path = os.path.join(directory, "merged_financial_terms.csv")
merged_df.to_csv(merged_csv_file_path, index=False)

print(f"Merged CSV file saved to {merged_csv_file_path}")