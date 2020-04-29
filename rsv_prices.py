

import pyodbc

driver = 'DRIVER={SQL Server}'
server = 'SERVER=10.20.193.20'
db = 'DATABASE=Energy'
user = 'UID=MinkinGR'
pw = 'PWD=+o,S=yLc'
conn_str = ';'.join([driver, server, db, user, pw])
 
conn = pyodbc.connect(conn_str)
# cursor = conn.cursor()
 
# cursor.execute('select * from table_name')
# row = cursor.fetchone()
# rest_of_rows = cursor.fetchall()