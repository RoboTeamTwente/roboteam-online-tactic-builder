# RoboTeam Tactic Builder
Welcome on the Tactic Builder repo. Relevant information regarding
installation, standards, design choices, protocols and can be found
[at the wiki](https://bitbucket.org/RoboSupportTeam/roboteam-tactic-builder/wiki/Home).

Please read the [Contribution Guide](https://bitbucket.org/RoboSupportTeam/roboteam-tactic-builder/wiki/Contribution/Guide.md) on the wiki before you start coding!

# Developing

## Creating the images

'''
docker build -t rtts-server -f Dockerserver .
'''

## Running the images

'''
docker run --name rtts-redis -d redis
docker run --name rtts-django --link rtts-redis:redis -d -p 8000:8000 rtts-server
docker run --name rtts-simulator --link rtts-redis:redis -d rtts_simulator
'''
