# Source for bot

### Setup without docker:
- Install python
- Install packages via `python -m pip install -r requirements.txt`
- Set discord token as environment variable
	- on Windows 
		- `set DISCORD_TOKEN=<your-token>`
		- or from file `set /P DISCORD_TOKEN=< <file_with_token.txt>`
		- check with `set DISCORD_TOKEN`
	- on Linux
		- `export DISCORD_TOKEN="<your_token>"`
		- check with `echo $DISCORD_TOKEN`


### Setup with docker:
- Create docker image
`docker image build -f Dockerfile -t ticks/discord-bot:0.0.1 --progress=plain`

- Check whether image is created
`docker images`

- Publish image
`docker image push ticks/discord-bot:0.0.1`

