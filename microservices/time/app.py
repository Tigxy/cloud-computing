import time
import requests
from flask import request, Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def service():
    return f"Today is {time.strftime('%A, %d.%m.%y. It is %H:%M:%S!')}"


if __name__ == "__main__":
    port = 7003
    registration_data = {
        "command": "time",
        "port": port
    }

    requests.post("http://localhost:7000/register", data=registration_data)
    print("Registered")

    app.run(host='0.0.0.0', port=port)
