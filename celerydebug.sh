# This turns on a local web management
# http://localhost:55672
grep_list=$(rabbitmq-plugins list rabbitmq_management -m -E | grep "rabbitmq_management$") 
echo "$grep_list"

if [ -z "$grep_list" ]
then
    echo "let's install the rabbitmq_management"
    sudo rabbitmq-plugins enable rabbitmq_management

    # restart the service
    sudo service rabbitmq-server restart
fi

# this turns on the celerybeat service
# this essentially watches the tasks and queues those mofos
# python manage.py celerybeat --logfile=./celerylog -l DEBUG

echo "Check out the web console http://localhost:55672/"
echo "Check out the web console http://localhost:55672/"
echo "Check out the web console http://localhost:55672/"
echo "Check out the web console http://localhost:55672/"
echo "Check out the web console http://localhost:55672/"

python manage.py celeryd -B --setting=settings


