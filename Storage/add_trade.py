from sqlalchemy import Column, Integer, String, DateTime, Boolean
import uuid
from base import Base
import datetime


class AddTrade(Base):

    __tablename__ = "Trade"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    tradeId = Column(String(250), nullable=False)
    tradeGrade = Column(Integer, nullable=False)
    tradeDec = Column(String(2), nullable=False)
    tradeImpact = Column(Integer, nullable=False)
    tradeProp = Column(String(250), nullable=False)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, tradeId, tradeGrade, tradeImpact, tradeProp , tradeDec, trace_id):
        self.tradeId = tradeId
        self.tradeGrade = tradeGrade
        self.tradeImpact = tradeImpact
        self.tradeProp = tradeProp
        self.tradeDec = tradeDec
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        dict = {}
        dict['ID'] = self.ID
        dict['tradeId'] = self.tradeId
        dict['tradeGrade'] = self.tradeGrade
        dict['tradeImpact'] = self.tradeImpact
        dict['tradeProp'] = self.tradeProp
        dict['tradeDec'] = self.tradeDec
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
