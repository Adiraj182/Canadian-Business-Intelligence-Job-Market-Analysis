import requests
import json
import pandas as pd
from datetime import datetime
import os
import time

os.makedirs("data", exist_ok=True)

API_KEY = "8dc9103f3fmsh6f82a9a3979f3a2p128898jsnd039d3ab8f15"
API_HOST = "jsearch.p.rapidapi.com"
URL = "https://jsearch.p.rapidapi.com/search"

cities = ["Toronto", "Ottawa", "Vancouver", "Montreal", "Calgary"]
roles = ["Data Analyst", "Business Intelligence", "Junior Data Engineer", "Business Intelligence Developer"]

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

records = []
print("Starting Job Search via RapidAPI (JSearch)...")

# RapidAPI free tier usually has a 50-100 request/month limit.
# 5 cities * 4 roles = 20 combinations. 
# Fetching 1 page (10 jobs) per query = 20 requests = 200 jobs.
# Fetching 2 pages (20 jobs) per query = 40 requests = 400 jobs limit.
# Let's fetch 1 page to definitely stay within safe limits while getting real data.

for city in cities:
    for role in roles:
        query = f"{role} in {city}, Canada"
        print(f"Fetching: {query}")
        
        querystring = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "country": "ca",
            "date_posted": "month"
        }
        
        try:
            response = requests.get(URL, headers=headers, params=querystring)
            data = response.json()
            
            if "data" in data:
                jobs = data["data"]
                print(f"  Found {len(jobs)} jobs.")
                
                for job in jobs:
                    # Extract skills roughly by checking descriptions 
                    # (since JSearch might not give a clean array of skills, we'll parse it later in Pandas, or just collect description)
                    # We will store the original description to parse later as per the requirement document.
                    desc = str(job.get("job_description", "")).lower()
                    
                    record = {
                        "job_id"         : job.get("job_id"),
                        "title"          : job.get("job_title"),
                        "company"        : job.get("employer_name"),
                        "city"           : job.get("job_city"),
                        "province"       : job.get("job_state"),
                        "salary_min"     : job.get("job_min_salary"),
                        "salary_max"     : job.get("job_max_salary"),
                        "job_type"       : job.get("job_employment_type"),
                        "remote_status"  : "Remote" if job.get("job_is_remote") else "On-site",
                        "pub_date"       : job.get("job_posted_at_datetime_utc"),
                        "job_apply_link" : job.get("job_apply_link", ""),
                        "scraped_on"     : datetime.now().isoformat(),
                        "job_description": job.get("job_description") # Crucial for Phase 2 skills extraction
                    }
                    records.append(record)
            else:
                print("  No 'data' in response or hit API limit:")
                print("  Response:", str(data)[:200])
                
            # Respect API limits
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error fetching {query}: {e}")

df = pd.DataFrame(records)
print(f"\nTotal scraped jobs from API: {len(df)}")

if len(df) > 0:
    df.drop_duplicates(subset=["job_id"], inplace=True)
    df.to_csv("data/job_postings_api_raw.csv", index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} unique postings to data/job_postings_api_raw.csv")
    print("Success! You have live data.")
else:
    print("No data collected... Check your API key limit.")
