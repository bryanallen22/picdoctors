#! /bin/bash

VENV_DIR=/srv/venvs
VENV_PROJ=django-picdoc

echo "====="
echo "Getting required system packages..."
echo "====="
# Used for PIL:
sudo apt-get install libjpeg8-dev -y
sudo apt-get install zlib1g-dev -y
sudo apt-get install libfreetype6-dev -y
sudo apt-get install liblcms2-dev -y
sudo apt-get install gcc -y
sudo apt-get install python2.7-dev -y

# Used for mysql (and python)
sudo apt-get install python-mysqldb libmysqlclient-dev -y

echo "====="
echo "Install pip"
echo "====="
sudo apt-get install python-pip -y
echo "====="
echo "Have pip update itself"
echo "====="
sudo pip install --upgrade pip

echo "====="
echo "Install virtualenv"
echo "====="
sudo pip install -U virtualenv

echo "====="
echo "Creating new virtualenv $VENV_DIR/$VENV_PROJ..."
echo "====="
sudo mkdir -p $VENV_DIR
if [ -e $VENV_DIR/$VENV_PROJ ]
then
  echo -n "$VENV_PROJ already exists! Delete? [y/n] "
  read answer
  if [ $answer = 'y' ]
  then
    sudo rm -rf $VENV_DIR/$VENV_PROJ
  else
    echo "Aborting!"
    exit 0
  fi
fi
sudo chown $USER:$USER $VENV_DIR
virtualenv $VENV_DIR/$VENV_PROJ

echo "====="
echo "Activating $VENV_DIR/$VENV_PROJ"
echo "====="
source $VENV_DIR/$VENV_PROJ/bin/activate

echo "====="
echo "Installing packages from requirements.txt"
echo "====="
pip install -r ../requirements.txt


echo "====="
echo "Installing npm, less, shint, recess, and uglify-js..."
echo "====="
sudo apt-get install npm -y
sudo npm install -g less jshint recess uglify-js yuglify

echo "====="
echo "Installing a crazy Rabbit Message Q"
echo "====="
sudo apt-get install rabbitmq-server -y
echo "stopping the rabbit"
sudo rabbitmq-server stop
echo "starting the rabbit"
sudo rabbitmq-server start
echo "setting up the rabbits user/pass/vhost"
sudo rabbitmqctl add_user weliketoeat rabbitsfordinner
sudo rabbitmqctl add_vhost carrot
sudo rabbitmqctl set_permissions -p carrot weliketoeat ".*" ".*" ".*"



echo "====="
echo "done."
echo "====="
