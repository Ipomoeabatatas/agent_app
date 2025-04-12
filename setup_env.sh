#!/bin/bash
#To use: 
#- chmod +x setup_env.sh
#- source setup_env.sh

# Define the project path
PROJECT_PATH="/home/tanpohkeam/ubts/agent_app/src"

# Add to PYTHONPATH if not already included
if [[ ":$PYTHONPATH:" != *":$PROJECT_PATH:"* ]]; then
    export PYTHONPATH="$PYTHONPATH:$PROJECT_PATH"
fi

# Add to PATH if not already included
if [[ ":$PATH:" != *":$PROJECT_PATH:"* ]]; then
    export PATH="$PATH:$PROJECT_PATH"
fi

## to fix this is not working
#export APP_CONFIG_PATH="/home/tanpohkeam/ubts/agent_app/config/app_config.toml"

# Display updated paths
#echo "Updated PYTHONPATH: $PYTHONPATH"
#echo "Updated PATH: $PATH"


## Get the development environment setup
export ENV_PATH="/home/tanpohkeam/ubts/agent_app/.env"
export APPCONFIG_PATH="/home/tanpohkeam/ubts/agent_app/config/app_config.toml"



env | grep PATH

source activate ubts

#jupyter notebook --no-browser --port=8966 &
