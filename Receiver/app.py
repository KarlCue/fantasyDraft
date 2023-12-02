import connexion
import yaml
import uuid
import logging
import logging.config
import datetime
import requests
import json
from pykafka import KafkaClient
from pykafka.exceptions import KafkaException
from connexion import NoContent
import time

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

MAX_EVENTS = 10
SERVICE_PORT = 8081
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

def kafka_init():
        max_retries = app_config['kafka']['max_retries']
        retry_wait = app_config['kafka']['retry_wait']
        retry_count = 0
        while retry_count < max_retries:
                try:
                        logger.info("Trying to connect to Kafka")
                        client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
                        topic = client.topics[str.encode(app_config['events']['topic'])]
                        producer = topic.get_sync_producer()
                        logger.info("Successfully connected to Kafka")
                        return client,producer
                except KafkaException:
                        logger.error(f"Unable to connect to Kafka, retrying in {retry_wait} seconds")
                        time.sleep(retry_wait)
                        retry_count += 1
        raise Exception("Maximum retries reached. Failed to connect to Kafka")

kafka_client,producer = kafka_init()
def add_pick(body):

    trace_id = str(uuid.uuid4())

    body["trace_id"] = trace_id

    logger.info(f'Received Pick request with trace id of {body["trace_id"]}')

    msg = { "type": "addPick",
    "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Returned Pick response (id: {body["trace_id"]}) with status code 201')

    return NoContent, 201

def add_trade(body):

    trace_id = str(uuid.uuid4())

    body["trace_id"] = trace_id

    logger.info(f'Received Pick request with trace id of {body["trace_id"]}')

    msg = { "type": "addTrade",
    "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Returned Pick response (id: {body["trace_id"]}) with status code 201')

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(YAML_FILE, 
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    app.run(port=SERVICE_PORT)