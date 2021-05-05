# This is a bash script. It is possible to run this manually to the same effect
# Just see MANUAL comments

#!/bin/bash 

# 1. First check to see if the correct version of Python is installed on the local machine 
echo "1. Checking Python version..."
REQ_PYTHON_V="370"

ACTUAL_PYTHON_V=$(python -c 'import sys; version=sys.version_info[:3]; print("{0}{1}{2}".format(*version))')
ACTUAL_PYTHON3_V=$(python3 -c 'import sys; version=sys.version_info[:3]; print("{0}{1}{2}".format(*version))')

if [[ $ACTUAL_PYTHON_V > $REQ_PYTHON_V ]] || [[ $ACTUAL_PYTHON_V == $REQ_PYTHON_V ]];  then 
    PYTHON="python"
elif [[ $ACTUAL_PYTHON3_V > $REQ_PYTHON_V ]] || [[ $ACTUAL_PYTHON3_V == $REQ_PYTHON_V ]]; then 
    PYTHON="python3"
else
    echo -e "\tPython 3.7 is not installed on this machine. Please install Python 3.7 before continuing."
    exit 1
fi

echo -e "\t--Python 3.7 is installed"

# 2. What OS are we running on?
PLATFORM=$($PYTHON -c 'import platform; print(platform.system())')

echo -e "2. Checking OS Platform..."
echo -e "\t--OS=Platform=$PLATFORM"

# 3. Create Virtual environment 
echo -e "3. Creating new virtual environment..."

# MANUAL: run 'Remove-Item env' in Powershell
# Remove the env directory if it exists 
if [[ -d env ]]; then 
    echo -e "\t--Virtual Environment already exists. Deleting old one now."
    rm -rf env  
fi

# MANUAL: run 'python -m venv env' or 'python3 -m venv env'
$PYTHON -m venv env  # Creates the virtual environment with name env
if [[ ! -d env ]]; then 
    echo -e "\t--Could not create virutal environment...Please make sure venv is installed"
    exit 1
fi

# 4. Install Requirements 

echo -e "4. Installing Requirements..."
if [[ ! -e "requirements.txt" ]]; then 
    echo -e "\t--Need to requirements.txt to install packages."
    exit 1
fi

# MANUAL Use '. .\env\scripts\activate' in Windows Powershell
source env/bin/activate # Activates the virtual environment 

# MANUAL Then run below command 
pip install -r requirements.txt

# 6. Install Selenium drivers (Notice I'm doing this will the virtual environment is activated!!)
# echo -e "5. Installing Selenium Drivers..."
# if [[ $PLATFORM == 'Linux' ]];  then 
#     wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz 
#     tar -xvf geckodriver-v0.29.0-linux64.tar.gz
#     mv geckodriver env/bin/ 
# fi
deactivate 
echo -e "Install is complete."

