import logging
import os
import time
import requests
from flask import request, Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def service():
    return f"Today is {time.strftime('%A, %d.%m.%y. It is %H:%M:%S!')}"


if __name__ == "__main__":

    port = os.environ.get('MICROSERVICE_PORT')

    if port is None:
        print("Env variable 'MICROSERVICE_PORT' not defined, exiting.")
        exit()

    ingress_host = os.environ.get("INGRESS_HOST")

    if not ingress_host:
        print("Ingress host configuration not found, exiting.")
        exit()

    registration_data = {
        "command": "time",
        "port": port
    }

    registered = False
    while not registered:
        try:
            requests.post(f"{ingress_host}/register", data=registration_data)
            registered = True
        except:
            print("Failed to register, trying again in 1 s")
            logging.warning("Failed to register, trying again in 1 s")
            time.sleep(10)

    print("Registered")
    logging.info("Registered")
    app.run(host='0.0.0.0', port=port)
