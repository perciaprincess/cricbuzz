🏏 Cricbuzz LiveStats: Real-Time SQL Analytics Dashboard

📌 Project Overview

Cricbuzz LiveStats is a dynamic cricket analytics platform built with Python, SQL, and Streamlit. It fetches live match data from the Cricbuzz API, stores it in a SQL database, and presents an interactive dashboard with real-time match insights, player statistics, and advanced SQL-driven analytics.

🚀 Key Features

- ⚡ Live Match Updates
Real-time scores, batsmen/bowler stats, match status, and venue details
- 📊 Player Analytics
Top scorers, highest wickets, batting & bowling averages with clean visualizations
- 🗄️ SQL Query Module
25+ beginner-to-advanced SQL queries for deep cricket insights
- ✏️ CRUD Operations
Add, update, delete, and view player/match stats via form-based UI
- 🖥️ Interactive Dashboard
Multi-page Streamlit app with sidebar navigation and responsive layout

🧰 Skills & Tools Used

- Python: pandas, requests, Streamlit
- SQL: MySQL, joins, indexing, CTE
- REST API: Cricbuzz (via RapidAPI)
- Web Development: Streamlit UI, data visualization, modular architecture

🏢 Business Applications

- Sports media & broadcasting
- Fantasy cricket platforms
- Cricket analytics firms
- Educational platforms for SQL & API learning
- Sports betting & performance prediction engines

📁 Project Structure

cricbuzz_livestats/                          
│── app.py                  
│── requirements.txt        
│── README.md                                            
│                                                                             
├── views/                  
│   ├── home.py         
│   ├── live_matches.py                        
│   ├── top_stats.py                          
│   ├── sql_queries.py                          
│   └── crud_operations.py                            
│                                                                                 
├── utils/                   
│   ├── db_connection.py                                                                               
│   ├── queries_mapping.py                                                                     
│                                                                                                         
└── notebooks/                                                                                                                                               
    └── data_fetching.ipynb

🧪 Getting Started

- Install dependencies
pip install -r requirements.txt
- Configure your database
- Edit utils/db_connection.py with your MySQL credentials
- Run the app
streamlit run app.py

🎯 Outcome

A fully functional, real-time cricket dashboard with
- Live match tracking
- Player analytics
- SQL practice module
- CRUD operations
Perfect for sports analytics enthusiasts, fantasy cricket platforms, and learners mastering SQL and API integration.
