# Canadian BI Job Market Analyzer 

An interactive, data-driven Business Intelligence dashboard built with Python and Streamlit. This application helps newcomers, international students, and recent graduates navigate the entry-level Data Science and Business Intelligence job market in Canada by synthesizing real-time job postings with socio-economic city data.

##  Features
- **Live Job Listings Explorer:** Filter and browse real-world job roles across major Canadian tech hubs (Toronto, Vancouver, Montreal, Calgary, Ottawa).
- **Map & City Analysis:** Interactive geographic bubble maps and heatmaps showing job volumes and industry distribution.
- **Skills Demand Analytics:** Horizontal bar charts outlining exactly which technical tools (SQL, Python, Power BI, etc.) yield the highest ROI for job seekers.
- **Opportunity Scorecap:** A custom KPI ranking cities holistically by weighing job availability against local median income and cost of living.
- **Newcomer Recommendations Engine:** Input your current skills and target role to dynamically calculate your "Skills Gap" and predict your median salary.

---

##  Project Architecture
The project operates via three decoupled layers:
1. **Extraction:** Python `.requests` fetching nested JSON arrays from the JSearch RapidAPI. 
2. **Processing (ETL):** Pandas logic (`clean_and_enrich_data.py`) parsing Regex Word Boundaries, normalizing strings, interpolating salaries, and merging CSVs files.
3. **Presentation:** Streamlit GUI (`app.py`) visualizing the flattened datasets using Plotly charts.

---

##  Installation & Setup

You need Python installed on your machine to run this project. 

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/CST2213_Project.git
cd CST2213_Project
```

### 2. Set Up a Virtual Environment (Recommended)
You may encounter a `"streamlit: command not found"` error if you try to run the app without installing the dependencies into a virtual environment.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On MacOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Make sure your virtual environment is activated, then install the required libraries:
```bash
pip install -r requirements.txt
```
*(If you do not have a requirements file, run: `pip install streamlit pandas plotly wordcloud matplotlib requests numpy`)*

---

##  How to Run the Application

Once your virtual environment is active and dependencies are installed, start the Streamlit server natively:

```bash
streamlit run app.py
```

* The dashboard will automatically open in your default web browser at `http://localhost:8501`.

### Manually Refreshing the Data
If you have a valid JSearch RapidAPI key, you can pull a fresh batch of data by running:
1. `python scripts/fetch_jobs_api.py`
2. `python scripts/clean_and_enrich_data.py`

---

##  Project Structure
```text
CST2213_Project/
│
├── app.py                             # Main Streamlit frontend dashboard
├── Project_Documentation.md           # Formal BI Technical Specifications
├── Data_Model_Star_Schema.md          # ER Diagram Database schemas
├── requirements.txt                   # Python package dependencies
│
├── data/                              # Local storage array
│   ├── city_data_raw.csv              # Static Census/Cost of Living data
│   ├── job_postings_api_raw.csv       # Raw JSON-converted API dump
│   └── job_postings_enriched.csv      # The final cleaned Fact Table powering the app
│
└── scripts/
    ├── fetch_jobs_api.py              # API Extraction Engine
    └── clean_and_enrich_data.py       # Pandas ETL / Cleaning Script
```

---
**Course:** CST2213  
**Status:** Final Submission
