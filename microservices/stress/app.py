import logging
from flask import request, Flask, Response
from multiprocessing import Pipe, Process
import os
import time

import requests

app = Flask(__name__)

@app.route("/stress", methods=["GET"])
def service():
    execute(request.args.get("data"))
    return "stress test finished"

@app.route("/stress/health", methods=["GET"])
def health():
    return Response(status=200)

def _spin(conn):
    proc_info = os.getpid()
    conn.send(proc_info)
    conn.close()

    while True:
        pass

def execute(query: str):
    # parse
    split = query.split()
    exec_time = int(split[0][:-1])

    if (split[0][-1] == "m"):
        exec_time *= 60
    elif split[0][-1] == "s":
        exec_time *= 1
    else:
        raise ValueError()

    num_processes = int(split[1][:-1])

    # start stress processes
    processes = [None] * num_processes
    connections = [None] * num_processes
    
    for i in range(num_processes):
        parent_conn, child_conn = Pipe()

        p = Process(target=_spin, args=(child_conn,))
        p.start()

        processes[i] = p
        connections[i] = parent_conn

    for conn in connections:
        try:
            print(conn.recv())
        except EOFError:
            continue

    time.sleep(exec_time)

    for p in processes:
        p.terminate()


if __name__ == "__main__":

    port = os.environ.get('MICROSERVICE_PORT')

    if port is None:
        print("Env variable 'MICROSERVICE_PORT' not defined, exiting.")
        exit()

    ingress_host = os.environ.get("INGRESS_HOST")

    if not ingress_host:
        print("Ingress host configuration not found, exiting.")
        exit()

    if ingress_host != "none":
        registration_data = {
            "command": "stress",
            "port": port
        }

        registered = False
        while not registered:
            try:
                requests.post(f"{ingress_host}/register", data=registration_data)
                registered = True
            except Exception as ex:
                print("Failed to register, trying again in 1 s")
                logging.warning("Failed to register, trying again in 10s")
                time.sleep(10)

        print("Registered")
        logging.info("Registered")
        
    app.run(host='0.0.0.0', port=port)