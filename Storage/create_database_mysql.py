import mysql.connector

db_conn = mysql.connector.connect(host="acit3855.eastus.cloudapp.azure.com", user="user", password='password', database='FantasyDraft')

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE Player
          (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
           playerId VARCHAR(250) NOT NULL, 
           playerName VARCHAR(250) NOT NULL,
           jerseyNum INTEGER NOT NULL,
           playerGrade VARCHAR(25) NOT NULL,
           plyTotalPoints INTEGER NOT NULL,
           playerTotalFanPts INTEGER NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

db_cursor.execute('''
          CREATE TABLE Trade
          (id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
           tradeId VARCHAR(250) NOT NULL,
           tradeProp VARCHAR(250) NOT NULL,
           tradeGrade VARCHAR(250) NOT NULL,
           tradeDec VARCHAR(2) NOT NULL,
           tradeImpact INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

db_conn.commit()
db_conn.close()

