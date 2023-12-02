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
from pykafka.exceptions import KafkaException
from threading import Thread
import json


current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")

MAX_EVENTS = 10
SERVICE_PORT = 8090
YAML_FILE = "fantasyLeague.yaml"
HOST = 'acit3855.eastus.cloudapp.azure.com:9092'

import os 

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

with open(app_conf_file, 'r') as f:
        app_config = yaml.safe_load(f.read())


with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['data']['user']}:{app_config['data']['password']}@{app_config['data']['hostname']}:{app_config['data']['port']}/{app_config['data']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logger.info(f"mysql database is running on HostName:{app_config['data']['hostname']} port{app_config['data']['port']}")

import time

def get_add_pick(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    readings = session.query(AddPick).filter(and_(AddPick.date_created >= start_timestamp_datetime, AddPick.date_created < end_timestamp_datetime))

    result_list = []

    for reading in readings:
        result_list.append(reading.to_dict())
    

    session.close()

    logger.info("Query for Draft Selections after %s returns %d results" % (start_timestamp, len(result_list)))

    return result_list, 200

def get_add_trade(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    readings = session.query(AddTrade).filter(and_(AddTrade.date_created >= start_timestamp_datetime, AddTrade.date_created < end_timestamp_datetime))

    result_list = []

    for reading in readings:
        result_list.append(reading.to_dict())
    

    session.close()

    logger.info("Query for Trades after %s returns %d results" % (start_timestamp, len(result_list)))

    return result_list, 200

def process_messages():
        """ Process event messages """
        max_retries = app_config["kafka"]["max_retries"]
        retry_wait = app_config["kafka"]["retry_wait"]
        hostname = HOST
        retry_count = 0
        client = None
        while retry_count < max_retries:
                try:
                        logger.info("Trying to connect to kafka")
                        client = KafkaClient(hosts=hostname)
                        topic = client.topics[str.encode(app_config["events"]["topic"])]
                        consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
                        logger.info("Successfully connected to kafka")
                        break
                except KafkaException:
                        logger.error(f"Unable to connect to kafka, retrying in {retry_wait} seconds")
                        time.sleep(retry_wait)
                        retry_count += 1
        if client is None:
                logger.error(f"Unable to connect to kafka after {max_retries} retries")
                return
        #client = KafkaClient(hosts=hostname)
        #topic = client.topics[str.encode(app_config["events"]["topic"])]

        for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
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
                    logger.debug(f"Stored pick with a trace id of {payload['trace_id']}")
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
                    logger.debug(f"Stored trade choice with a trace id of {payload['trace_id']}")
                        
                else:
                        logger.error("Received event with unknown type")
                consumer.commit_offsets()

        logger.warn("Shutdown of consumer thread complete")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(YAML_FILE, 
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=SERVICE_PORT)

