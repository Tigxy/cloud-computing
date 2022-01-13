import logging
import os
import time

import discord
import asyncio
import requests
from threading import Thread

from aiohttp import ClientConnectorError
from flask import request, Flask, Response
from urllib.parse import urlencode

INGRESS_HOST = os.environ.get('INGRESS_HOST', None)
BOT_COMMAND_PREFIX = os.environ.get('BOT_COMMAND_PREFIX', None)

# Dictionary that is dynamically built up when microservices register, contains service: endpoint mapping
# Ignore thread safety for now as write accesses shouldn't happen very often
service_dict = {}


def configure_registration_endpoint(app):
    global service_dict

    app.debug = False
    app.use_reloader = False

    @app.route("/register", methods=["GET"])
    def hello():
        return "main is working"

    @app.route("/register", methods=["POST"])
    def service():
        logging.info("Received registration from: %s", request.remote_addr)
        command = request.form.get("command")
        port = request.form.get("port")

        # only register service if it has provided required fields
        if command and port:
            service_dict[command] = f"http://{request.remote_addr}:{port}"
            logging.info("Registered service for command '%s' on '%s'", command, service_dict[command])
            return "OK"
        return "NOK"

    @app.route("/register/health", methods=["GET"])
    def health():
        return Response(status=200)


def configure_discord_client(client, prefix="!"):
    global service_dict

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        # Bot shouldn't trigger its own messages
        if message.author == client.user:
            return

        logging.info("Received message on '%s' in '%s' from '%s'", message.guild, message.channel, message.author)

        msg = message.content.strip()
        if not msg.startswith(prefix):
            logging.warning("Received message does not contain defined prefix: %s", prefix)
            return

        # get command without prefix
        command = msg.split(" ")[0][1:]
        arguments = msg[len(command) + 2:]  # account for prefix and white space

        if command == "help":
            service_commands = [prefix + "help"] + [prefix + k for k in service_dict.keys()]
            await message.channel.send("Possible commands: " + ", ".join(service_commands))

        # Pass command to respective microservice
        elif command in service_dict.keys():
            try:
                r = requests.get(INGRESS_HOST + command + "?" + urlencode({"data": arguments}))
                await message.channel.send(r.content.decode('utf8'))
            except Exception:
                await message.channel.send("Failed to execute command. Please check whether service is "
                                           "still available and try again.")

        else:
            await message.channel.send("Unknown command!")

    print("Discord client is configured.")


# TODO: Periodically check whether services are still available
async def command_services_health_check():

    global service_dict
    logging.info("Running command services health check")
    services = service_dict.copy()
    for service in services:
        response = requests.get(f"{INGRESS_HOST}/{service}/health")
        if not response.ok:
            service_dict.pop(service)
            logging.info("Deregistered service for command '%s'", service)

    await asyncio.sleep(60)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    if not INGRESS_HOST:
        logging.error("INGRESS_HOST not defined via environment variable.. exiting")
        exit()

    token = os.environ.get('DISCORD_TOKEN')

    if not token:
        print("Please provide a discord access token by setting the 'DISCORD_TOKEN' environment variable!")
        print("Exiting.")
        logging.error("DISCORD_TOKEN not defined via environment variable.. exiting")
        exit()

    port = os.environ.get('SERVICE_PORT')

    if not port:
        print("Port not defined via environment variable, exiting.")
        logging.error("SERVICE_PORT not defined via environment variable.. exiting")
        exit()

    # checkout https://stackoverflow.com/a/55054500 for problem description

    try:
        client = discord.Client()

        if BOT_COMMAND_PREFIX:
            configure_discord_client(client, BOT_COMMAND_PREFIX)
        else:
            configure_discord_client(client)

        loop = asyncio.get_event_loop()
        loop.create_task(client.start(token))
        discord_thread = Thread(target=loop.run_forever)
        discord_thread.start()

        app = Flask(__name__)
        configure_registration_endpoint(app)
        loop = asyncio.get_event_loop()
        loop.create_task(app.run(host='0.0.0.0', port=port))
        registration_thread = Thread(target=loop.run_forever)
        registration_thread.start()

        loop = asyncio.get_event_loop()
        loop.create_task(command_services_health_check())
        health_check_thread = Thread(target=loop.run_forever())
        health_check_thread.start()

        discord_thread.join()
        registration_thread.join()
        health_check_thread.join()
    except (discord.errors.LoginFailure, ClientConnectorError) as ex:
        logging.error("Exception: %s", ex)
