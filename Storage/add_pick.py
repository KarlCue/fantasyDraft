from sqlalchemy import Column, Integer, String, DateTime
import uuid
from base import Base
import datetime


class AddPick(Base):

    __tablename__ = "Player"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    playerId = Column(String(250), nullable=False)
    playerName = Column(String(250), nullable=False)
    jerseyNum = Column(Integer, nullable=False)
    playerGrade = Column(String(15), nullable=False)
    plyTotalPoints = Column(Integer, nullable=False)
    playerTotalFanPts = Column(Integer, nullable=False)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, playerId, playerName, jerseyNum, playerGrade, plyTotalPoints, playerTotalFanPts, trace_id):
        self.playerId = playerId
        self.playerName = playerName
        self.jerseyNum = jerseyNum
        self.playerGrade = playerGrade
        self.plyTotalPoints = plyTotalPoints
        self.playerTotalFanPts = playerTotalFanPts
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        dict = {}
        dict['ID'] = self.ID
        dict['playerId'] = self.playerId
        dict['playerName'] = self.playerName
        dict['jerseyNum'] = self.jerseyNum
        dict['playerGrade'] = self.playerGrade
        dict['plyTotalPoints']= self.plyTotalPoints
        dict['playerTotalFanPts']= self.playerTotalFanPts
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
