import datetime
import json
from kafka import KafkaProducer
import random
import time
import uuid
from faker import Faker

faker = Faker()

EVENT_TYPE_LIST = ['buy', 'click', 'hover', 'idle_5']

producer = KafkaProducer(
   value_serializer=lambda msg: json.dumps(msg).encode('utf-8'), # we serialize our data to json for efficent transfer
#    bootstrap_servers=['kafka1:9091','kafka2:9092','kafka3:9093'],
   bootstrap_servers=['localhost:9092'],
   key_serializer=str.encode)

TOPIC_NAME = 'events_topic'

start_date = datetime.date(2021, 10, 1)
end_date = datetime.date(2021, 12, 15)

time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days

PRODUCT_LIST=[f'product{i:0>2}' for i in range(1,11)]
USERNAMES=[ faker.user_name() for x in range(1000)]


def _produce_event():
    """
    Function to produce events
    """
    # UUID produces a universally unique identifier
    random_number_of_days = random.randrange(days_between_dates)
    random_date= (start_date + datetime.timedelta(days=random_number_of_days)).isoformat()
    
    return {
        'event_id': str(uuid.uuid4()),
        'event_datetime': random_date , #datetime.datetime.now().isoformat(),
        'event_type': random.choice(EVENT_TYPE_LIST),
        'product_id': random.choice(PRODUCT_LIST),
        'event_value' : round(random.random() * 10_000,3),
        'user_name': random.choice(USERNAMES),
        'page': faker.uri_path()
    }

def send_events():
    cnt = 0
    while(True):
        data = _produce_event()
        time.sleep(0.5) # simulate some processing logic
        producer.send(TOPIC_NAME, value=data, key=data['event_id'])
        print(f"#{cnt:5} - Event Created : {data['event_id']}- Value : {data['event_value']}")
        cnt=cnt+1


if __name__ == '__main__':
    send_events()