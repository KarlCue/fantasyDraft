import connexion
import yaml
import requests
import logging
import logging.config
import json
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import datetime
from flask_cors import CORS, cross_origin

SERVICE_PORT = 8100
YAML_FILE = 'fantasyLeague.yaml'

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")

import os 

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
        app_config = yaml.safe_load(f.read())


with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def get_stats():

    logger.info("Request has Started")

    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)

        response_data = {
                    "draft_selection": stats["draft_selection"],
                    "trade_moves" : stats["trade_moves"],
                    "maxPoints" : stats["maxPoints"],
                    "totalPoints" : stats["totalPoints"],
                    "last_updated" :  current_datetime_str
                    }

        logger.debug(f"Statistics Response: {response_data}")

        logger.info("Requests for statistics has completed")

        return response_data,200

    except:
        logger.error("File does not exist")
        return 404, "Statistics do not exist"
    
    


def populate_stats():
    try:
        logging.info("Periodic processing has started.")

        try:
            with open(app_config['datastore']['filename'], 'r') as config_file:
                stats = json.load(config_file)

        except:
            stats = {
                    "draft_selection": 0,
                    "trade_moves" : 0,
                    "maxPoints" : 0,
                    "totalPoints" : 0,
                    "last_updated" :  current_datetime_str
                    }
                
            with open(app_config['datastore']['filename'], 'w') as config_file:
                json.dump(stats, config_file)
        
        current_time = stats['last_updated']
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        pick = requests.get(f"{app_config['eventstore']['url']}/game/draft/readings", params={"start_timestamp" : current_time , "end_timestamp" : current_timestamp})
        trade = requests.get(f"{app_config['eventstore']['url']}/game/trades/readings", params={"start_timestamp" : current_time , "end_timestamp" : current_timestamp})
        data = pick.json()
        if pick.status_code == 200 and trade.status_code == 200:
            picks = len(pick.json())
            trades = len(trade.json())
            max_points = max([event['plyTotalPoints'] for event in data])
            total_points = sum([event['plyTotalPoints'] for event in data])
            total_events_received = picks + trades
            logging.info(f"Received {total_events_received} new events.")
        else:
            logging.error("Failed to fetch events from Storage Service.")


        stats["draft_selection"] = picks
        stats["trade_moves"] = trades
        stats["maxPoints"] = max_points
        stats["totalPoints"] = total_points
        stats["last_updated"] = current_time

        with open(app_config['datastore']['filename'], 'w') as config_file:
            json.dump(stats, config_file)

        logging.debug(f"Updated statistics: Drafts={picks}, Trades={trades}")

        logging.info("Periodic processing has ended.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(YAML_FILE, 
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=SERVICE_PORT)