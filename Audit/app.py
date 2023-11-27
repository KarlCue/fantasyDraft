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
from flask_cors import CORS, cross_origin

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

MAX_EVENTS = 10
SERVICE_PORT = 8110
YAML_FILE = "fantasyLeague.yaml"
CONF_YML = 'app_conf.yml'
LOG_YML = 'log_conf.yml'

with open (CONF_YML, "r") as f:
    app_config = yaml.safe_load(f.read())

with open (LOG_YML, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def add_pick(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("retrieve selection %d" % index)
    try:
        events = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get("type") == "addPick":
                events.append(msg)
                if len(events) > int(index):
                    logger.info("Found selections at index %d" % int(index))
                    return events[int(index)], 200

    except:
        logger.error("No more messages found")
    logger.error("Could not find selection at index %d" % int(index))
    return { "message": "Not Found"}, 404


def add_trade(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("retrieve trade %d" % index)
    try:
        events = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg.get("type") == "addTrade":
                events.append(msg)
                if len(events) > int(index):
                    logger.info("Found trades at index %d" % int(index))
                    return events[int(index)], 200

    except:
        logger.error("No more messages found")
    logger.error("Could not find trade at index %d" % int(index))
    return { "message": "Not Found"}, 404



app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(YAML_FILE, 
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    app.run(port=SERVICE_PORT)