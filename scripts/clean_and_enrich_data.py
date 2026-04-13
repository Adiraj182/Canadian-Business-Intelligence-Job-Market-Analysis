import os
import pandas as pd
import numpy as np
import re

# Ensure the script/notebook strictly executes from the project root
if os.path.basename(os.getcwd()) in ['scripts', 'notebooks']:
    os.chdir('..')
import os

print("Starting Data Cleaning and Enrichment Process...")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# 1. Load Data
# We check which raw file exists. If the API one exists, we use it, otherwise the mock one.
if os.path.exists("data/job_postings_api_raw.csv"):
    jobs_df = pd.read_csv("data/job_postings_api_raw.csv")
elif os.path.exists("data/job_postings_raw.csv"):
    jobs_df = pd.read_csv("data/job_postings_raw.csv")
else:
    raise FileNotFoundError("Could not find raw job postings CSV.")

city_df = pd.read_csv("data/city_data_raw.csv")
print(f"Loaded {len(jobs_df)} job postings and {len(city_df)} city records.")

# 2. Standardize Job Titles
def standardize_title(title):
    if not isinstance(title, str): return "Other"
    title_lower = title.lower()
    if "data analyst" in title_lower or "data analytics" in title_lower:
        return "Data Analyst"
    elif "engineer" in title_lower and "data" in title_lower:
        return "Data Engineer"
    elif "business intelligence" in title_lower or "bi " in title_lower:
        if "developer" in title_lower:
            return "BI Developer"
        return "BI Analyst"
    elif "scientist" in title_lower:
        return "Data Scientist"
    return "Other Data Role"

jobs_df['Standardized_Title'] = jobs_df['title'].apply(standardize_title)

# 3. Normalize City (Handle variations)
def normalize_city(city):
    if not isinstance(city, str): return "Unknown"
    c = city.lower()
    if "toronto" in c or "gta" in c or "mississauga" in c or "brampton" in c: return "Toronto"
    if "vancouver" in c or "burnaby" in c or "richmond" in c: return "Vancouver"
    if "montreal" in c or "montréal" in c or "laval" in c: return "Montreal"
    if "calgary" in c: return "Calgary"
    if "ottawa" in c or "kanata" in c or "gatineau" in c: return "Ottawa"
    return city.title()

jobs_df['Normalized_City'] = jobs_df['city'].apply(normalize_city)

# Filter out jobs not in our 5 target cities
target_cities = ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"]
jobs_df = jobs_df[jobs_df['Normalized_City'].isin(target_cities)].copy()

# 4. Clean Salary Data
def parse_salary(row):
    # If using JSearch API, there are min and max columns
    if 'salary_min' in row and pd.notna(row['salary_min']):
        return row['salary_min'], row['salary_max']
    
    # If using string salary from mock or scraping
    if 'salary' in row and isinstance(row['salary'], str):
        sal_str = row['salary'].replace(',', '').replace('$', '')
        nums = re.findall(r'\d+', sal_str)
        if len(nums) >= 2:
            return float(nums[0]), float(nums[1])
        elif len(nums) == 1:
            return float(nums[0]), float(nums[0])
            
    return np.nan, np.nan

if 'salary' in jobs_df.columns or 'salary_min' in jobs_df.columns:
    salaries = jobs_df.apply(parse_salary, axis=1)
    jobs_df['Clean_Salary_Min'] = [s[0] for s in salaries]
    jobs_df['Clean_Salary_Max'] = [s[1] for s in salaries]
    jobs_df['Clean_Salary_Mid'] = (jobs_df['Clean_Salary_Min'] + jobs_df['Clean_Salary_Max']) / 2
else:
    jobs_df['Clean_Salary_Min'] = np.nan
    jobs_df['Clean_Salary_Max'] = np.nan
    jobs_df['Clean_Salary_Mid'] = np.nan

# 5. Extract Skills
# List of technical skills to check
target_skills = ['SQL', 'Python', 'Power BI', 'Tableau', 'Excel', 'Azure', 'AWS', 'GCP', 'Snowflake', 'R']

# Create a combined text field to search in
jobs_df['Search_Text'] = jobs_df['title'].astype(str)
if 'job_description' in jobs_df.columns:
    jobs_df['Search_Text'] += " " + jobs_df['job_description'].astype(str)
elif 'skills_required' in jobs_df.columns:
    jobs_df['Search_Text'] += " " + jobs_df['skills_required'].astype(str)

for skill in target_skills:
    # Use word boundary regex for exact matching (e.g., matching 'R' but not 'Requirements')
    if skill.lower() == 'r':
        pattern = r'\b[rR]\b'
    elif skill.lower() == 'power bi':
        pattern = r'(?i)\bpower\s*bi\b'
    else:
        # Escape special characters
        escaped_skill = re.escape(skill)
        pattern = rf'(?i)\b{escaped_skill}\b'
        
    jobs_df[f'Skill_{skill.replace(" ", "")}'] = jobs_df['Search_Text'].str.contains(pattern, regex=True).fillna(False).astype(int)


# 6. Standardize Remote Status
if 'remote_status' in jobs_df.columns:
    def clean_remote(val):
        if not isinstance(val, str): return "On-site"
        val = val.lower()
        if 'remote' in val or 'work from home' in val: return "Remote"
        if 'hybrid' in val: return "Hybrid"
        return "On-site"
    jobs_df['Standardized_Remote'] = jobs_df['remote_status'].apply(clean_remote)

# 7. Drop invalid records and cleanup columns
# Keep essential columns
cols_to_keep = ['job_id', 'title', 'Standardized_Title', 'company', 'Normalized_City']
if 'province' in jobs_df.columns: cols_to_keep.append('province')

curr_cols = jobs_df.columns.tolist()
for c in ['Clean_Salary_Min', 'Clean_Salary_Max', 'Clean_Salary_Mid', 'Standardized_Remote', 'job_type', 'pub_date', 'job_description']:
    if c in curr_cols: cols_to_keep.append(c)

skill_cols = [c for c in curr_cols if c.startswith('Skill_')]
cols_to_keep.extend(skill_cols)

final_jobs_df = jobs_df[[c for c in cols_to_keep if c in jobs_df.columns]].copy()

# Output Clean Data
final_jobs_df.to_csv("data/job_postings_cleaned.csv", index=False)
print(f"Saved {len(final_jobs_df)} cleaned job postings to data/job_postings_cleaned.csv")

# 8. Merge Jobs with City Data (Enrichment)
enriched_df = pd.merge(final_jobs_df, city_df, left_on='Normalized_City', right_on='City', how='left')
enriched_df.drop('City', axis=1, inplace=True) # Drop duplicate City column

# Create Opportunity Score metric directly here so it exists in the CSV
# Opportunity Score = (Job Count factor) * (Salary Income factor) / (Cost of Living factor)
# We will do a simple relative score mapping:
city_job_counts = enriched_df['Normalized_City'].value_counts()
enriched_df['City_Job_Volume'] = enriched_df['Normalized_City'].map(city_job_counts)

# Let's normalize metrics for a simple 1-10 Opportunity Score approximation
max_vol = enriched_df['City_Job_Volume'].max()
max_sal = enriched_df['Median_Household_Income'].max()
max_cpi = enriched_df['Cost_Of_Living_Index'].max()

# Formula: (Volume/Max_Vol) * (Income/Max_Inc) / (CPI/Max_CPI) * 10
enriched_df['Opportunity_Score'] = (
    (enriched_df['City_Job_Volume'] / max_vol) * 
    (enriched_df['Median_Household_Income'] / max_sal) / 
    (enriched_df['Cost_Of_Living_Index'] / max_cpi) * 10
).round(2)

enriched_df.to_csv("data/job_postings_enriched.csv", index=False)
print(f"Saved enriched data to data/job_postings_enriched.csv")

print("\nData pipeline completed successfully!")
