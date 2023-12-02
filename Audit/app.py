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


def add_pick(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("retrieve selection %d" % index)

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            # Check if the event type matches and decrement index until it reaches 0
            if msg.get("type") == "addPick":
                if index == 0:
                    return msg, 200
                index -= 1

        # If no event found at the specified index
        return {"message": "Not Found"}, 404

    except Exception as e:
        return {"message": "Internal Server Error"}, 500


def add_trade(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("retrieve selection %d" % index)
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            # Check if the event type matches and decrement index until it reaches 0
            if msg.get("type") == "addTrade":
                if index == 0:
                    return msg, 200
                index -= 1

        # If no event found at the specified index
        return {"message": "Not Found"}, 404

    except Exception as e:
        return {"message": "Internal Server Error"}, 500


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