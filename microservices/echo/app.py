import requests
from flask import request, Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def service():
    return request.args.get("data")


if __name__ == "__main__":
    port = 7002
    registration_data = {
        "command": "echo",
        "port": port
    }

    requests.post("http://localhost:7000/register", data=registration_data)
    print("Registered")

    app.run(host='0.0.0.0', port=port)
