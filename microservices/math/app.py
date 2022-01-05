import logging
import os
import time
import requests
from pycalc import solve
from flask import request, Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def service():
    formula = request.args.get("data")
    try:
        result = str(solve(formula))
    except ValueError as err:
        result = f"Failed to perform calculation: {err}"
    return result


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
        "command": "math",
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
            time.sleep(1)

    print("Registered")
    logging.info("Registered")
    app.run(host='0.0.0.0', port=port)