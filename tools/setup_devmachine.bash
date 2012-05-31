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
echo "====="
echo "====="
echo "====="
echo "====="
echo "====="
echo "====="
echo "====="
echo "====="
