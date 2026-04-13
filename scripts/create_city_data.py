import pandas as pd
import os

os.makedirs("data", exist_ok=True)

# Data based on Statistics Canada 2021 Census, Numbeo 2024 Estimates, and recent Labour Force Surveys
# Target cities: Ottawa, Toronto, Montreal, Vancouver, Calgary

data = [
    {
        "City": "Toronto",
        "Province": "ON",
        "Population": 6202225, # CMA
        "Unemployment_Rate_Pct": 7.4, # Recent estimate
        "Median_Household_Income": 97000, 
        "Average_Rent_1BR_CAD": 2500, # Approx Numbeo/Rentals.ca
        "Cost_Of_Living_Index": 73.2, 
        "Number_of_Universities": 4
    },
    {
        "City": "Vancouver",
        "Province": "BC",
        "Population": 2642825, # CMA
        "Unemployment_Rate_Pct": 5.9,
        "Median_Household_Income": 90000,
        "Average_Rent_1BR_CAD": 2700,
        "Cost_Of_Living_Index": 74.5,
        "Number_of_Universities": 3
    },
    {
        "City": "Montreal",
        "Province": "QC",
        "Population": 4291732, # CMA
        "Unemployment_Rate_Pct": 6.8,
        "Median_Household_Income": 82000,
        "Average_Rent_1BR_CAD": 1700,
        "Cost_Of_Living_Index": 64.8,
        "Number_of_Universities": 4
    },
    {
        "City": "Calgary",
        "Province": "AB",
        "Population": 1481806, # CMA
        "Unemployment_Rate_Pct": 6.1,
        "Median_Household_Income": 105000,
        "Average_Rent_1BR_CAD": 1900,
        "Cost_Of_Living_Index": 68.2,
        "Number_of_Universities": 3
    },
    {
        "City": "Ottawa",
        "Province": "ON",
        "Population": 1488307, # CMA
        "Unemployment_Rate_Pct": 5.5,
        "Median_Household_Income": 102000,
        "Average_Rent_1BR_CAD": 2000,
        "Cost_Of_Living_Index": 67.5,
        "Number_of_Universities": 2
    }
]

df = pd.DataFrame(data)
output_path = "data/city_data_raw.csv"
df.to_csv(output_path, index=False)

print(f"Successfully generated city socio-economic data for {len(df)} cities!")
print(f"Data saved to {output_path}")
print("\nSnapshot of data:")
print(df.head())
