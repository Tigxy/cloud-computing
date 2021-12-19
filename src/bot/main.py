import os
import re
import time
import math
import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"Received message on '{message.guild}' in '{message.channel}' from '{message.author}'")

    msg = message.content
    if msg == "!help":
        await message.channel.send(f"Possible commands: !help, !echo, !time, !pi, !math")

    elif msg.startswith("!echo"):
        await message.channel.send(msg[len('!echo '):])

    elif msg == "!time":
        await message.channel.send(f"Today is {time.strftime('%A, %d.%m.%y. It is %H:%M:%S!')}")

    elif msg == "!pi":
        await message.channel.send(f"{math.pi:.40f}...")

    elif msg.startswith("!math"):
        s = msg[len("!math "):]
        operators = ['/', '*', '-', '+']
        chars = re.findall(rf"([0-9.]+|[{''.join(operators)}])", s)

        # convert actual values to float
        chars = [float(c) if c.isnumeric() else c for c in chars]

        if len(chars) == 0:
            await message.channel.send(f"State your formula.")
            return

        pos_ops = [c in operators for c in chars]

        # ensure that formula doesn't start with an operator
        if pos_ops[0] in operators or pos_ops[-1] in operators:
            await message.channel.send(f"Invalid formula.")

        # ensure that there is a number between operators
        prev_was_op = True
        for i in pos_ops[:-1]:
            if i in operators and prev_was_op:
                await message.channel.send(f"Invalid formula.")
                return
            prev_was_op = i in operators

        result = chars.copy()

        cdots = 0
        for i, c in enumerate(result):
            if c in ["/", "*"]:
                k = i - 2 * cdots
                result[k] = result[k-1] * result[k+1] if c == "*" else result[k-1] / result[k+1]
                del result[k+1]
                del result[k-1]
                cdots += 1

        while len(result) > 1:
            sign = -1 if result[1] == "-" else 1
            result[0] += sign * result[2]
            del result[1]
            del result[1]

        await message.channel.send(f"Result is {result[0]:.2f}")

    else:
        await message.channel.send(f"Unknown command!")

token = os.environ.get('DISCORD_TOKEN')

if not token:
	print("Please provide a discord access token by setting the 'DISCORD_TOKEN' environment variable!")
	print("Exiting.")
	exit()

client.run(token)



