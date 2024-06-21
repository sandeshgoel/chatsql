# Import required libraries 
import sqlite3 
import pandas as pd 

# Connect to SQLite database 
conn = sqlite3.connect('Ramen.db') 

def create_table(table, csv):
    print('\nCreating table %s from file %s\n' % (table, csv))
    # Load CSV data into Pandas DataFrame 
    data = pd.read_csv(csv) 
    # Write the data to a sqlite table 
    data.to_sql(table, conn, if_exists='replace', index=False) 

    # Create a cursor object 
    cur = conn.cursor() 
    # Fetch and display result 
    for row in cur.execute('SELECT * FROM ' + table): 
        print(row) 


create_table('customers', 'data/cust_data.csv')
create_table('cameras', 'data/camera_data.csv')
create_table('alerts', 'data/alert_data.csv')

# Close connection to SQLite database
conn.close() 
