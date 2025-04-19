#!/bin/bash
#To use: 
#- chmod +x setup_env.sh
#- source setup_env.sh


############################################
# TODO: Updateproject path
###########################################

PROJECT_PATH="/home/tanpohkeam/ubts/agent_app/src"
export ENV_PATH="/home/tanpohkeam/ubts/agent_app/.env"
export APPCONFIG_PATH="/home/tanpohkeam/ubts/agent_app/config/app_config.toml"


echo " "
echo "** You should see 4 paths set "
echo "** Make sure it points to your local environment "
echo "ENV_PATH is $ENV_PATH"
echo "APPCONFIG_PATH is $ENV_PATH"

############################################
### DO NOT CHANGE ANYTHING BELOW
############################################

# Add to PYTHONPATH if not already included
if [[ ":$PYTHONPATH:" != *":$PROJECT_PATH:"* ]]; then
    export PYTHONPATH="$PYTHONPATH:$PROJECT_PATH"
fi

# Add to PATH if not already included
if [[ ":$PATH:" != *":$PROJECT_PATH:"* ]]; then
    export PATH="$PATH:$PROJECT_PATH"
fi

echo "PATHONPATH is $PYTHONPATH"
echo "PATH is $PATH"
echo " "

#############################################3
# source activate ubts

#jupyter notebook --no-browser --port=8966 &
