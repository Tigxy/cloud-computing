from flask import Flask

app = Flask(__name__)

@app.route("/<query>")
def hello_world(query):
    execute(query)
    return "done"

from multiprocessing import Pipe, Process
import os
import time

def _spin(conn):
    proc_info = os.getpid()
    conn.send(proc_info)
    conn.close()

    while True:
        pass

def execute(query: str):
    # parse
    split = query.split()
    exec_time = int(split[1][:-1])

    if (split[1][-1] == "m"):
        exec_time *= 60
    elif split[1][-1] == "s":
        exec_time *= 1
    else:
        raise ValueError()

    num_processes = int(split[2][:-1])

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