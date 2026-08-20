# ETL Pipeline Project (Dockerized)

This projects implements a config-driven ETL pipleline that extracts data from multiple sources(file directory/DB table/API), validates it and loads it into a database.

## Project details - Architecture

Extract -> Transform -> Load

- EXTRACT : 

    1. "DB_intregation.py" python script - reads data from database and writes
         .csv to "data/files_input" folder
    2. "file_integration" python scipt - reads data from other local files to "data/files_input"
        folder
    3. "API_integration" python scipt - fetches data from API and writes data to "data/files_input" folder.

- TRANSFORM : 

    Data is validated based on control vs data files. If validation fails - files are moved to "data/files_error" folder.

- LOAD : 

    If validated correctly, moves the files to db table (Raw -> Validated) and then to "data/files_processed" folder.

- main.py : 

    runs every 30secs and continuoulsy scans "data/files_input" folder.


## setup
- pip3 install --no-cache-dir -r requirements.txt
- python3 scipts/main.py    

## Python files
- Assignment/scripts/API_integration.py
- Assignment/scripts/DB_integration.py
- Assignment/scripts/file_integration.py
- Assignment/scripts/main.py

## Run with Docker
docker build -t etl-pipleline
docker run --env-file .env etl-pipleine

## Features
- Multi source ingestion(file, db, API)
- config driveb onboarding
- Validation
- Dockerized deployement