# Information and instructions for running the bot

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
  `docker image build -t ticks/discord-bot:0.0.1 .`

- Check whether image is created  
  `docker images`

- Test image, note that the `env_file.txt` must contain a key-value pair for `DISCORD_TOKEN`.  
  `docker container run --env-file <env_file.txt> ticks/discord-bot:0.0.1`

- Publish image  
  `docker image push ticks/discord-bot:0.0.1`


### Starting with minikube:
- Starting minikube with restriction on resources  
  `minikube start --memory 2048 --cpus 2`

- Check whether local kubernetis is actually running  
  `kubectl cluster-info`

- Starts pods  
  `kubectl apply -f .\pods.yaml`  
  Note: Replace the `DISCORD_TOKEN` placeholder with the actual token!

- Stop pods  
  `kubectl delete pods discord-service`

- Stop minikube, can also be used to then start it again with other restriction on resources  
  `minikube stop`