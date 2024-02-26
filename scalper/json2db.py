import os
import re
import json
import sys
import shutil
import mysql.connector

def main(symbol):
    # Compiled regular expression for performance
    pattern = re.compile(rf'{symbol}_(\d{{8}})\.json')
    
    # Database configuration
    db_config = {
        'user': 'upbit_sim',
        'password': 'Upbit1234!',
        'host': '127.0.0.1',
        'database': 'upbit_sim'
    }

    # Directory paths
    input_directory = '/workspace/scalper_server/data'
    output_directory = os.path.join('/workspace/scalper_server/data', symbol)

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Collect all valid file paths and dates
    file_list = [(os.path.join(input_directory, f), int(pattern.match(f).group(1)))
                 for f in os.listdir(input_directory)
                 if pattern.match(f)]

    # Sort files by date
    file_list.sort(key=lambda x: x[1])

    # Process each file
    try:
        with mysql.connector.connect(**db_config) as cnx, cnx.cursor() as cursor:
            add_data = (f"INSERT IGNORE INTO upbit_"+symbol+" "
                        "(name, price, trend, trend_price, time) "
                        "VALUES (%s, %s, %s, %s, %s)")
            
            for filepath, _ in file_list:
                process_file(filepath, cursor, add_data)
                # Move processed file
                shutil.move(filepath, os.path.join(output_directory, os.path.basename(filepath)))
                cnx.commit()

    except Exception as e:
        print("An error occurred:", e)

def process_file(filepath, cursor, add_data):
    with open(filepath, 'r') as file:
        data = json.load(file)
        for entry in data:
            cursor.execute(add_data, (entry[1], entry[2], entry[3], entry[4], entry[5]))
    print(f"Processed {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\tError) Enter the Symbol ")
        print("\tEX) $ py 파일명.py [SYMBOL] ")
        sys.exit()
    main(sys.argv[1])


"""
This Python script is designed to process and migrate JSON files containing financial data into a MySQL database, specifically tailored for a system dealing with cryptocurrency data. Here's a detailed breakdown of its usage, features, and expected outcomes:

Usage:
Command Line Execution: To run the script, use the following command format in a terminal:

python json2db.py [SYMBOL]
Here, [SYMBOL] should be replaced with the actual symbol of the cryptocurrency you are interested in (e.g., BTC, ETH).

Features:
1. Import Necessary Modules: The script begins by importing modules for operating system interaction (os), regular expressions (re), JSON file handling (json), system-specific parameters and functions (sys), file operations (shutil), and MySQL database connection (mysql.connector).

2. Main Function: The script defines a main function which takes symbol as an argument. This symbol specifies the cryptocurrency and is used to identify relevant files and database tables.

3. Regular Expression Compilation: It uses a compiled regular expression to match file names that correspond to the provided cryptocurrency symbol followed by a date in the format YYYYMMDD.json. This is used to filter relevant files in the input directory.

4. Database Configuration: It sets up the configuration for connecting to the MySQL database with specified user credentials and database name (upbit_sim).

5. Directory Paths: It defines the input and output directory paths for the JSON files.

6. File Sorting: The script collects all files that match the symbol pattern, extracts their dates, and sorts them in ascending order based on date.

7. Database Connection and Processing: The script opens a connection to the database and processes each file one by one. For each file:

 - It reads the JSON data.
 - Each entry from the JSON file is inserted into the database using the INSERT IGNORE INTO statement (ignores if the same entry already exists).
 - After processing, the file is moved to an output directory.

8. Error Handling: It includes basic error handling, catching exceptions during database operations or file handling and printing an error message.

9. Argument Checking: The script checks if the symbol argument is provided when the script is executed. If not, it prints an error message and exits.

Expected Outcomes:
1. Database Update: For each JSON file that matches the pattern and date criteria, the script inserts data into the specified table in the MySQL database (upbit_<symbol>). This table will be filled with rows representing financial data from the JSON files, such as name, price, trend, etc.

2. File Management: After processing each JSON file, the script moves it from the input directory to the output directory. This helps in keeping track of which files have been processed.

3. Error Messages: If any issue occurs during the database connection or file handling, the script will print an error message detailing the problem.

4. Exit on Missing Argument: If the script is run without the required symbol argument, it prints usage instructions and exits without attempting to process any files.

Use Case:
Automating Data Transfer: This script is useful in a system where new JSON files with financial data are regularly created (e.g., daily market summaries) and need to be consistently added to a database for record-keeping, analysis, or display purposes.

Conclusion:
This Python script efficiently organizes and inserts cryptocurrency data from JSON files into a MySQL database, automating what could otherwise be a tedious manual process. It's structured to handle errors gracefully and requires minimal user input, making it suitable for automated scripts or systems handling financial data analysis or tracking.
"""