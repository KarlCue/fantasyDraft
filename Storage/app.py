import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import yaml
import logging.config
from base import Base
from add_pick import AddPick
from add_trade import AddTrade
import datetime

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json


current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")

MAX_EVENTS = 10
SERVICE_PORT = 8090
YAML_FILE = "fantasyLeague.yaml"
CONF_YML = 'app_conf.yml'
LOG_YML = 'log_conf.yml'
HOST = 'acit3855.eastus.cloudapp.azure.com:9092'

with open (CONF_YML, "r") as f:
    app_config = yaml.safe_load(f.read())

with open (LOG_YML, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['data']['user']}:{app_config['data']['password']}@{app_config['data']['hostname']}:{app_config['data']['port']}/{app_config['data']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logger.info(f"mysql database is running on HostName:{app_config['data']['hostname']} port{app_config['data']['port']}")


def get_add_pick(timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

    readings = session.query(AddPick).filter(AddPick.date_created >= timestamp_datetime)

    result_list = []

    for reading in readings:
        result_list.append(reading.to_dict())
    

    session.close()

    logger.info("Query for Draft Selections after %s returns %d results" % (timestamp, len(result_list)))

    return result_list, 200

def get_add_trade(timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

    readings = session.query(AddTrade).filter(AddTrade.date_created >= timestamp_datetime)

    result_list = []

    for reading in readings:
        result_list.append(reading.to_dict())
    

    session.close()

    logger.info("Query for Trades after %s returns %d results" % (timestamp, len(result_list)))

    return result_list, 200

def process_messages():

    client = KafkaClient(hosts=HOST)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "addPick": 
            session = DB_SESSION()
            pick = AddPick(payload['playerId'],
                        payload['playerName'],
                        payload['jerseyNum'],
                        payload['playerGrade'],
                        payload['playerTotalFanPts'],
                        payload['plyTotalPoint'],
                        payload['trace_id'])

            session.add(pick)
            
            session.commit()
            session.close()

            logger.debug(f"Stored Pick request with the a trace id of {payload['trace_id']}")

        elif msg["type"] == "addTrade": 
            
            session = DB_SESSION()

            trade = AddTrade(payload['tradeId'],
                        payload['tradeGrade'],
                        payload['tradeImpact'],
                        payload['tradeProp'],
                        payload['tradeDec'],
                        payload['trace_id'])

            session.add(trade)
            session.commit()
            session.close()

            logger.debug(f"Stored Trade request with the a trace id of {payload['trace_id']}")
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(YAML_FILE, 
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=SERVICE_PORT)

