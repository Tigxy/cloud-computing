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
    port = 7001
    registration_data = {
        "command": "math",
        "port": port
    }

    requests.post("http://localhost:7000/register", data=registration_data)
    app.run(host='0.0.0.0', port=port)
