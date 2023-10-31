import connexion
import yaml
import uuid
import logging
import logging.config
import datetime
import requests
import json
from pykafka import KafkaClient
from connexion import NoContent

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

MAX_EVENTS = 10
SERVICE_PORT = 8080
YAML_FILE = "fantasyLeague.yaml"
CONF_YML = 'app_conf.yml'
LOG_YML = 'log_conf.yml'

with open (CONF_YML, "r") as f:
    app_config = yaml.safe_load(f.read())

with open (LOG_YML, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def add_pick(body):

    trace_id = str(uuid.uuid4())

    body["trace_id"] = trace_id

    logger.info(f'Received Pick request with trace id of {body["trace_id"]}')

    client = KafkaClient(hosts='ec2-52-42-191-123.us-west-2.compute.amazonaws.com:9092')
    topic = client.topics[str.encode('FantasyDraft')]
    producer = topic.get_sync_producer()
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

    client = KafkaClient(hosts='ec2-52-42-191-123.us-west-2.compute.amazonaws.com:9092')
    topic = client.topics[str.encode('FantasyDraft')]
    producer = topic.get_sync_producer()
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