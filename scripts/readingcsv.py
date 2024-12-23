import os
import csv

# Define the output path for the merged CSV file
merged_csv_path = '/home/greenbaum-gpu/Reuben/CellDetection/finaloutput/annotations.csv'

# Open the merged CSV file for writing
with open(merged_csv_path, mode='w', newline='') as merged_file:
    writer = csv.writer(merged_file)

    # Iterate through all the individual CSV files in the csv_output folder
    for csv_file in os.listdir('/home/greenbaum-gpu/Reuben/CellDetection/output/csv_output'):
        if csv_file.endswith('_result.csv'):
            # Open each individual CSV file
            with open(os.path.join('/home/greenbaum-gpu/Reuben/CellDetection/output/csv_output', csv_file), mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row
                for row in reader:
                    # Write the row to the merged CSV
                    writer.writerow(row)
