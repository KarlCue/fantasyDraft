import mysql.connector

db_conn = mysql.connector.connect(host="acit3855.eastus.cloudapp.azure.com", user="user",
password="password", database="FantasyDraft")

db_cursor = db_conn.cursor()
db_cursor.execute('''
 DROP TABLE Player, Trade 
''')

db_conn.commit()
db_conn.close()