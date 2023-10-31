import mysql.connector

db_conn = mysql.connector.connect(host="ec2-52-42-191-123.us-west-2.compute.amazonaws.com", user="user",
password="password", database="FantasyDraft")

db_cursor = db_conn.cursor()
db_cursor.execute('''
 DROP TABLE Player, Trade 
''')

db_conn.commit()
db_conn.close()