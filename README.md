# 🏡 Real Estate Price Analysis and Prediction 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huy-real-estate-prediction.streamlit.app/)

A comprehensive Data Science project focusing on the analysis and prediction of real estate prices in Vietnam's four major markets: **Hanoi, Da Nang, Ho Chi Minh City, and Binh Duong**. 

This project was developed for the **ADY201m** course at FPT University.

---

## 👥 Group Members
| Student ID | Name | Role/Tasks |
| :--- | :--- | :--- |
| **SE201725** | Nguyen Gia Huy | Data Processing, Visualization, Modeling |
| **SE203377** | Tran Canh Nhat Minh | Data Scrubbing, Standardization |
| **SE204049** | Nguyen Xuan Binh | Feature Engineering, Model Tuning |
| **SE201652** | Dang Thai Nguyen | Exploratory Data Analysis, Interpretation |

## 🎯 Project Objectives
- **Analysis:** Explore the relationships between property prices and key attributes (area, location, amenities, legal status). Identify pricing trends across different regions and evaluate market distribution.
- **Prediction:** Build a robust machine learning model to estimate property values based on historical data and spatial insights, providing an objective reference price for both buyers and sellers.

## 📊 Dataset \& Features
The data was collected by web crawling property listings from *batdongsan.com.vn* and enhanced with geospatial amenity data from *OpenStreetMap (OSM)*. 

After rigorous data cleaning and feature engineering, the final model utilizes **17 key features** grouped into:
1. **Target:** `price_total`, `price_per_m2`
2. **Location:** Province, District, Latitude, Longitude.
3. **Property Characteristics:** Area, Category, Legal Status, Frontage, Road Width, Number of Bedrooms, Toilets, and Floors.
4. **External Amenities:** Density of Schools (within 1km), Hospitals (2km), and Markets/Supermarkets (1km).

## 🛠️ Methodology \& Tech Stack
The project workflow strictly follows the **OSEMN** framework (Obtain $\rightarrow$ Scrub $\rightarrow$ Explore $\rightarrow$ Model $\rightarrow$ iNterpret).

* **Language \& Processing:** Python, Pandas, NumPy, SQL
* **Visualization:** Matplotlib, Seaborn
* **Machine Learning:** Scikit-Learn, XGBoost, LightGBM, CatBoost
* **Deployment:** Streamlit, Folium
* **APIs:** OpenStreetMap (OSM), Nominatim, Overpass API

## 🧠 Modeling \& Results
We evaluated 5 different regression models to predict property values. 

The **Extra Trees (Extremely Randomized Trees)** algorithm outperformed the others, achieving the highest **$R^2$ score of 0.84**. It successfully captured non-linear relationships between a property's location, surrounding amenities, and its physical attributes. We selected this algorithm as our core prediction model.

## 📁 Repository Structure
```text
📦 real-estate-price-analysis
 ┣ 📂 data              # Raw, processed data, and mapping data
 ┣ 📂 scrape            # Automated web crawling scripts for listings
 ┣ 📂 process_data      # Data cleaning, formatting, and standardizing scripts
 ┣ 📂 visualization     # Exploratory Data Analysis (EDA) & insightful charts
 ┣ 📂 regression        # ML model training, evaluation, and hyperparameter tuning
 ┣ 📂 real_estate_app   # Source code for the interactive Streamlit Web App
 ┣ 📂 final_report      # Complete LaTeX project report and final docs
 ┣ 📂 mini_report       # Interim and phase-based project reporting
 ┗ 📂 geojson           # Geographical boundary boundaries for maps
```

## 🚀 Try the Live App
We deployed an interactive web application integrating our trained Extra Trees model and a smart interactive map. Select a location, see local amenities, and get an instant AI-powered real estate valuation!

👉 **[Live Demo: Real Estate Price Prediction App](https://huy-real-estate-prediction.streamlit.app/)**
