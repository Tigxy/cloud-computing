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

    main_service_url = os.environ.get("MAIN_DISCORD_SERVICE_HOST")
    main_service_port = os.environ.get("MAIN_DISCORD_SERVICE_PORT")
    if main_service_url is None or main_service_url is None:
        print("Main Discord service configuration not found, exiting.")
        exit()

    registration_data = {
        "command": "math",
        "port": port
    }

    not_registered = True
    while not_registered:
        try:
            requests.post(f"http://{main_service_url}:{main_service_port}/register", data=registration_data)
            not_registered = False
        except:
            print("Failed to register, trying again in 1 s")
            time.sleep(1)

    print("Registered")
    app.run(host='0.0.0.0', port=port)
