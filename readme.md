# ETL Pipeline Project

## Project details
Extract -> Transform -> Load

- Extract : PostgreSQL - sourceDB(pg_db_jan) - Python reads table and writes it into .csv in files_input folder/reads from files/reads from API call.
- Transform : Based on conditions, moves the files to error or processed folder. And appends data to output folder files with extra columns (creation & processed timestamps)
- Load : Loads the output folder files to new database (redshift_db) tables.

## setup
- pip3 install -r requirements.txt

## Python files
- Assignment/scripts/convert_fetchDB.py
- Assignment/scripts/convert_fetchfiles.py
- Assignment/scripts/writeto_redshiftDB.py
- Assignment/scripts/read_from_api.py