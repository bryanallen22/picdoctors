#! /bin/bash

VENV_DIR=/srv/venvs
VENV_PROJ=django-picdoc

echo "Is $(pwd) -- where you are now -- the top of the project? [y/n]"
read istop
if [ $istop != "y" ]; then
    echo "please cd there and run this script from there"
    exit 1
fi

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
#sudo apt-get install python-mysqldb libmysqlclient-dev -y
sudo apt-get install libpq-dev postgresql-contrib postgresql -y

# Used for django-extensions
sudo apt-get install libgraphviz-dev graphviz pkg-config

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
sudo npm install -g django-ember-precompile
npm install yuglify # hopefully you are already sitting at the top level of the project, else this will be in the wrong place

echo "====="
echo "done."
echo "====="
