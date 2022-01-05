import logging
import os
import discord
import asyncio
import requests
from threading import Thread
from flask import request, Flask
from urllib.parse import urlencode


INGRESS_HOST = os.environ.get('INGRESS_HOST', None)

# Dictionary that is dynamically built up when microservices register, contains service: endpoint mapping
# Ignore thread safety for now as write accesses shouldn't happen very often
service_dict = {}

# TODO: Periodically check whether services are still available

def configure_registration_endpoint(app):
    global service_dict

    app.debug = False
    app.use_reloader = False

    @app.route("/", methods=["GET"])
    def hello():
        return "main is working"

    @app.route("/", methods=["POST"])
    def service():
        print("Received registration from", request.remote_addr)
        logging.warning(f"Received registration from: {request.remote_addr}")
        command = request.form.get("command")
        port = request.form.get("port")

        # only register service if it provided required fields
        if command and port:
            service_dict[command] = f"http://{request.remote_addr}:{port}"
            print(f"Registered service for command '{command}' on '{service_dict[command]}'")
            logging.warning(f"Registered service for command '{command}' on '{service_dict[command]}'")
            return "OK"
        return "NOK"


def configure_discord_client(client):
    global service_dict

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(message):
        # Bot shouldn't trigger its own messages
        if message.author == client.user:
            return
        print(f"Received message on '{message.guild}' in '{message.channel}' from '{message.author}'")
        logging.warning(f"Received message on '{message.guild}' in '{message.channel}' from '{message.author}'")


        msg = message.content.strip()
        if not msg.startswith("!"):
            return

        # get command without '!'
        command = msg.split(" ")[0][1:]
        arguments = msg[len(command) + 2:]  # account for '!' and white space

        if command == "help":
            service_commands = ["!help"] + ["!" + k for k in service_dict.keys()]
            await message.channel.send("Possible commands: " + ", ".join(service_commands))

        # Pass command to respective microservice
        elif command in service_dict.keys():
            try:
                r = requests.get(INGRESS_HOST +  command + "?" + urlencode({"data": arguments}))
                await message.channel.send(r.content.decode('utf8'))
            except:
                await message.channel.send("Failed to execute command. Please check whether service is "
                                           "still available and try again.")

        else:
            await message.channel.send("Unknown command!")

    print("Discord client is configured.")


if __name__ == "__main__":

    if not INGRESS_HOST:
            logging.error("INGRESS_URL not defined via environment variable.. exiting")
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

    client = discord.Client()
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

    #discord_thread.join()
    registration_thread.join()
