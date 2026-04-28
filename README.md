#  Smart Volunteer Allocation System

##  Overview
The **Smart Volunteer Allocation System** is an AI-based web application designed to help NGOs efficiently assign volunteers to community needs.  
It uses data-driven logic to match the **right volunteer to the right task at the right time**.

---

##  Problem Statement
NGOs often face challenges such as:
- Unstructured and scattered data  
- Difficulty in prioritizing urgent issues  
- Inefficient manual volunteer assignment  

This system solves these problems using **automated matching and visualization**.

---

##  Features

-  Add and manage community issues  
-  Add and manage volunteer data  
-  Load dataset from Excel  
-  Smart volunteer matching (AI-like scoring)  
-  Interactive dashboard (analytics)  
-   Advanced map visualization (PyDeck)  
-   Issue ↔ Volunteer connection lines  
-   History management (view & delete records)  

---

##  How It Works

1. Data is collected from:
   - NGO inputs (issues)
   - Volunteer dataset (Excel)

2. Stored in:
   - SQLite database

3. Matching algorithm:
   - Skill match → 50%
   - Location match → 30%
   - Availability → 20%

4. Output:
   - Best volunteer assigned to each issue  
   - Visualized on dashboard and map  

---

##  Tech Stack

- **Frontend & Backend:** Streamlit  
- **Database:** SQLite  
- **Data Processing:** Pandas  
- **Map Visualization:** PyDeck  
- **Language:** Python  

---

## 📂 Project Structure
GOOGLE_SOLUTION/
│
├── app.py
├── utils/
│ └── matcher.py
├── dataset/
│ └── Volunteer-match.xlsx
├── database/
│ └── data.db
