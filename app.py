import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="Canadian BI Job Market Analysis", page_icon="🍁", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stMetric .metric-value {color: #1f77b4; font-size: 2rem !important; font-weight: bold;}
    h1, h2, h3 {color: #2c3e50;}
    .reportview-container .main .block-container {max-width: 1200px;}
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        # Load the enriched data
        df = pd.read_csv("data/job_postings_enriched.csv")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Project Overview", 
    "Map & City Analysis", 
    "Job Listings Explorer",
    "Skills Demand", 
    "Opportunity Scorecap", 
    "Newcomer Recommendations"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**CST2213 BI Project**\n\n*Interactive Dashboard*")

if page == "Project Overview":
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
    st.title("Canadian BI Job Market Analyzer")
    st.markdown("""
    Welcome to the **Business Intelligence Job Market Dashboard**. 
    
    This portal analyzes recent Canadian job postings along with city-level socio-economic data to guide international students and newcomers in choosing optimal cities, roles, and skills for entry-level data careers in Canada.
    """)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Job Postings", len(df))
    col2.metric("Cities Analyzed", df['Normalized_City'].nunique())
    col3.metric("Avg. Salary (Est.)", f"${df['Clean_Salary_Mid'].mean():,.0f}")
    
    remote_pct = (df['Standardized_Remote'].isin(['Remote', 'Hybrid']).sum() / len(df)) * 100
    col4.metric("Remote/Hybrid Roles", f"{remote_pct:.1f}%")

    st.markdown("### Raw Data Preview")
    st.dataframe(df[['title', 'company', 'Normalized_City', 'Standardized_Remote', 'Clean_Salary_Mid', 'pub_date']].head(10))

elif page == "Map & City Analysis":
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
    st.title("Opportunities by City and Role")
    
    # 1. Interactive Map
    st.subheader("Interactive Job Map")
    st.markdown("Scroll and zoom to explore job density across major Canadian tech hubs.")
    
    # Coordinates dictionary
    city_coords = {
        "Toronto": {"lat": 43.651070, "lon": -79.347015},
        "Vancouver": {"lat": 49.2827, "lon": -123.1207},
        "Montreal": {"lat": 45.5017, "lon": -73.5673},
        "Calgary": {"lat": 51.0447, "lon": -114.0719},
        "Ottawa": {"lat": 45.4215, "lon": -75.6972}
    }
    
    city_counts = df['Normalized_City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Job Count']
    
    # Merge coords
    city_counts['lat'] = city_counts['City'].map(lambda c: city_coords.get(c, {}).get('lat', 56.1304))
    city_counts['lon'] = city_counts['City'].map(lambda c: city_coords.get(c, {}).get('lon', -106.3468))
    
    fig_map = px.scatter_mapbox(
        city_counts, lat="lat", lon="lon", size="Job Count", color="Job Count",
        hover_name="City", hover_data=["Job Count"],
        color_continuous_scale=px.colors.sequential.Plasma, size_max=40,
        zoom=3, center={"lat": 55.0, "lon": -95.0},
        mapbox_style="carto-positron"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Job Volume by City")
        fig1 = px.bar(city_counts, x='City', y='Job Count', color='City', text='Job Count', 
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Job Volume by Role")
        role_counts = df['Standardized_Title'].value_counts().reset_index()
        role_counts.columns = ['Role', 'Job Count']
        fig2 = px.pie(role_counts, values='Job Count', names='Role', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("City vs Role Heatmap")
    heatmap_data = pd.crosstab(df['Normalized_City'], df['Standardized_Title'])
    fig3 = px.imshow(heatmap_data, text_auto=True, color_continuous_scale="Blues", aspect="auto")
    st.plotly_chart(fig3, use_container_width=True)

elif page == "Skills Demand":
    st.title("Top Skills in Demand")
    
    # Filter for standard skills extracted dynamically
    skill_cols = [c for c in df.columns if c.startswith('Skill_')]
    skills_sums = df[skill_cols].sum().sort_values(ascending=False).reset_index()
    skills_sums.columns = ['Skill', 'Frequency']
    skills_sums['Skill'] = skills_sums['Skill'].str.replace('Skill_', '').str.replace('PowerBI', 'Power BI')
    skills_sums['Percentage'] = (skills_sums['Frequency'] / len(df)) * 100

    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(skills_sums, x='Percentage', y='Skill', orientation='h',
                     title="Percentage of Postings Requiring Skill",
                     color='Percentage', color_continuous_scale="Viridis")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### Key Insights")
        st.info(f"The most requested skill is **{skills_sums.iloc[0]['Skill']}**, appearing in {skills_sums.iloc[0]['Percentage']:.1f}% of all job postings.")
        st.info(f"**{skills_sums.iloc[1]['Skill']}** is the second most crucial tool to learn.")

    # Skills by City filter
    st.subheader("Explore Skills by City")
    selected_city = st.selectbox("Select a City", df['Normalized_City'].unique())
    
    city_df = df[df['Normalized_City'] == selected_city]
    c_skills = city_df[skill_cols].sum().reset_index()
    c_skills.columns = ['Skill', 'Count']
    c_skills['Skill'] = c_skills['Skill'].str.replace('Skill_', '')
    c_skills = c_skills.sort_values(by='Count', ascending=False).head(5)
    
    st.write(f"Top 5 required skills for Data roles in **{selected_city}**:")
    st.bar_chart(c_skills.set_index('Skill'))

elif page == "Opportunity Scorecap":
    st.title("True Cost-of-Living Opportunity Score")
    
    st.markdown("""
    The **Opportunity Score** evaluates how favorable a city really is by looking beyond raw job volume.
    It combines:
    * Job Availability
    * Median Income
    * Cost of Living Index (Inverse)
    """)
    
    # Get one row per city since demographic/score is duplicated for every job posting
    city_metrics = df[['Normalized_City', 'Population', 'Median_Household_Income', 'Cost_Of_Living_Index', 'City_Job_Volume', 'Opportunity_Score']].drop_duplicates()
    city_metrics = city_metrics.sort_values('Opportunity_Score', ascending=False)
    
    fig = px.bar(city_metrics, x='Normalized_City', y='Opportunity_Score', text='Opportunity_Score',
                 color='Opportunity_Score', color_continuous_scale="Teal",
                 title="Overall City Opportunity Score (1-10 Rank)")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Underlying City Metrics")
    st.dataframe(city_metrics.reset_index(drop=True))

elif page == "Newcomer Recommendations":
    st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
    st.title("Optimal Career Path Engine")
    
    st.markdown("Use this tool to evaluate the best career pathway based on your specific skills and work preferences as a newcomer.")
    
    col1, col2 = st.columns(2)
    with col1:
        role_options = ["Any"] + list(df['Standardized_Title'].unique())
        preferred_role = st.selectbox("Select your target entry-level role:", role_options)
        preferred_work_type = st.radio("Preferred Work Environment:", ["Any", "Remote", "Hybrid", "On-site"])
        
    with col2:
        available_skills = [c.replace("Skill_", "") for c in df.columns if c.startswith("Skill_")]
        top_skills = st.multiselect("Select your strongest technical skills:", available_skills, default=[available_skills[0]])
        preferred_cities = st.multiselect("Preferred Cities (Leave blank for all of Canada):", df['Normalized_City'].unique())

    # Filter engine
    if preferred_role == "Any":
        filtered_df = df.copy()
    else:
        filtered_df = df[df['Standardized_Title'] == preferred_role].copy()
    
    if preferred_work_type != "Any":
        filtered_df = filtered_df[filtered_df['Standardized_Remote'] == preferred_work_type]
        
    if len(preferred_cities) > 0:
        filtered_df = filtered_df[filtered_df['Normalized_City'].isin(preferred_cities)]
        
    for skill in top_skills:
        filtered_df = filtered_df[filtered_df[f'Skill_{skill}'] == 1]
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("No postings found perfectly matching this exact combination. Consider broadening your requirements or acquiring additional skills.")
    else:
        st.success(f"Discovered {len(filtered_df)} exact opportunities matching your custom profile.")
        
        # --- NEW FEATURE: SALARY PREDICTOR & SKILL GAP ANALYZER ---
        st.markdown("### 🤖 Advanced Predictive Analytics")
        metrics_col1, metrics_col2 = st.columns(2)
        
        # 1. Salary Predictor
        with metrics_col1:
            avg_min = filtered_df['Clean_Salary_Min'].mean()
            avg_max = filtered_df['Clean_Salary_Max'].mean()
            if pd.notna(avg_min) and avg_min > 0:
                st.metric(label="💰 Predicted Market Salary Range", value=f"${avg_min:,.0f} - ${avg_max:,.0f}")
            else:
                st.metric(label="💰 Predicted Market Salary Range", value="Salary data hidden by employers")
                
        # 2. Missing Skills Gap Analyzer
        with metrics_col2:
            other_skills = [s for s in available_skills if s not in top_skills]
            if other_skills and len(filtered_df) > 0:
                skill_counts = {s: filtered_df[f'Skill_{s}'].sum() for s in other_skills}
                best_missing = max(skill_counts, key=skill_counts.get)
                count_miss = skill_counts[best_missing]
                if count_miss > 0:
                    pct = (count_miss / len(filtered_df)) * 100
                    st.warning(f"**Skills Gap Identified:** {pct:.0f}% of these matching jobs ALSO require **{best_missing}**. Acquiring `{best_missing}` next will drastically maximize your resume's impact!")
                else:
                    st.success("You possess all major tracked skills for these specific jobs!")

        st.markdown("---")
        # ---------------------------------------------------------
        
        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            best_cities = filtered_df['Normalized_City'].value_counts().reset_index()
            best_cities.columns = ['City', 'Job Count']
            fig = px.pie(best_cities, values='Job Count', names='City', hole=0.3, title="Job Distribution by City for Your Profile")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_res2:
            st.markdown("### AI Recommendation")
            top_city = best_cities.iloc[0]['City']
            
            # Retrieve the Opportunity Score
            city_score = df[df['Normalized_City'] == top_city]['Opportunity_Score'].iloc[0]
            
            st.write(f"Based strictly on the volume of active requirements for your selected skills (`{', '.join(top_skills)}`), **{top_city}** is the statistically optimal target.")
            st.info(f"The macroeconomic Opportunity Score for {top_city} stands at **{city_score:.1f}/10**.")
        
        st.subheader("Explore Recommended Positions:")
        st.dataframe(filtered_df[['title', 'company', 'Normalized_City', 'Clean_Salary_Mid', 'Standardized_Remote']].head(10))

elif page == "Job Listings Explorer":
    st.image("https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
    st.title("Live Job Listings Explorer")
    st.markdown("Filter and browse through the active job postings. Expand any row to read the description and find application links.")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    c_filter = col1.selectbox("Filter by City", ["All"] + list(df['Normalized_City'].unique()))
    r_filter = col2.selectbox("Filter by Role", ["All"] + list(df['Standardized_Title'].unique()))
    w_filter = col3.selectbox("Work Type", ["All"] + list(df['Standardized_Remote'].unique()))
    
    filtered = df.copy()
    if c_filter != "All": filtered = filtered[filtered['Normalized_City'] == c_filter]
    if r_filter != "All": filtered = filtered[filtered['Standardized_Title'] == r_filter]
    if w_filter != "All": filtered = filtered[filtered['Standardized_Remote'] == w_filter]
    
    
    st.write(f"Showing **{len(filtered)}** matching roles.")
    
    if len(filtered) > 0:
        # --- NEW FEATURE: CSV EXPORT BUTTON ---
        csv_data = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download This Custom Data Report (CSV)", 
            data=csv_data, 
            file_name='custom_bi_job_report.csv', 
            mime='text/csv'
        )
        
        # --- NEW FEATURE: WORD CLOUD ---
        with st.expander("☁️ View Industry Buzzword Cloud (from Job Descriptions)"):
            text_data = " ".join(filtered['job_description'].dropna().astype(str).tolist())
            if len(text_data) > 50:
                # Basic exclusion list for word cloud
                stopwords_list = set(["and", "the", "to", "of", "a", "in", "is", "for", "with", "this", "we", "on", "you", "are", "by", "as", "an"])
                wordcloud = WordCloud(width=800, height=350, background_color='white', stopwords=stopwords_list, colormap='magma').generate(text_data)
                fig_wc, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig_wc)
            else:
                st.write("Not enough description data to generate a word cloud.")
                
    st.markdown("---")

    # Display individual jobs
    for idx, row in filtered.head(20).iterrows(): # Show top 20 to keep it clean
        with st.expander(f"{row['title']} at {row['company']} ({row['Normalized_City']})"):
            st.markdown(f"**Company:** {row['company']}")
            st.markdown(f"**Location:** {row['Normalized_City']} | **Type:** {row['Standardized_Remote']}")
            
            salary_display = f"${row['Clean_Salary_Min']:,.0f} - ${row['Clean_Salary_Max']:,.0f}" if pd.notna(row['Clean_Salary_Min']) else "Not Disclosed"
            st.markdown(f"**Estimated Salary:** {salary_display}")
            
            st.markdown(f"**Description Snippet:**")
            desc = str(row.get('job_description', "No Description Provided"))
            st.info(desc[:500] + "..." if len(desc) > 500 else desc)
            
            search_query = f"{row['title']} {row['company']} {row['Normalized_City']} apply".replace(" ", "+")
            st.markdown(f"[**Click here to search and apply on Google Jobs**](https://www.google.ca/search?q={search_query})")
    
    if len(filtered) > 20:
        st.caption(f"... and {len(filtered)-20} more. Adjust filters to narrow down your search criteria.")

