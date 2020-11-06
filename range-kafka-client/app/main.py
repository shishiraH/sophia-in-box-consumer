import os
import json
from kafka_client import get_consumer, config
from util import get_limit_timetamp, get_readable_date
from confluent_kafka import OFFSET_END, KafkaError, KafkaException
from confluent_kafka.avro.serializer import SerializerError
from config import (
    MESSAGE_KEY_FIELD,
    CHOSEN_GROUP_TOPIC,
    WAIT_TIME,
    MAX_WAIT_TIMES
)


def get_topic_dict():
    topic_dict = {}
    for topic in CHOSEN_GROUP_TOPIC:
        topic_dict[topic] = []

    return topic_dict


def on_assign(consumer, partitions):
    for p in partitions:
        p.offset = OFFSET_END
    consumer.assign(partitions)


def consume():
    topic_dict = get_topic_dict()
    print('topic_dict',topic_dict)
    yesterday, today = get_limit_timetamp()
    consumer = get_consumer()

    list_of_topic = [CHOSEN_GROUP_TOPIC]
    print("Chosen topic...",list_of_topic)
    consumer.subscribe(list_of_topic, on_assign=on_assign)
    count_times = 0
    running = True
    try:
        while running:
            message = consumer.poll(10)
            if message is None:
                # print("continue ....")
                # continue
                print("Waiting for message or event/error in poll()")
                count_times += 1
                print("Reach " + str(count_times) + " times, " + str(MAX_WAIT_TIMES - count_times) + " remaining")

                if count_times == MAX_WAIT_TIMES:
                    running = False
                else:
                    continue
            elif message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    print(message.error().code())
                    #running = False
                elif message.error():
                    raise KafkaException(message.error())
            else:
                print('<SHISHIR>')
                compare_ts = message.timestamp()[1]
                print(get_readable_date(compare_ts) + ' || Key: ' + str(message.key()) + ' || Offset: ' + str(message.offset()) +  ' || Partition: ' + str(message.partition()) + ' - ' + message.topic())
                print(message.value())

                if message.value():
                    topic_dict[message.topic()].append(message.value())

    except SerializerError as e:
        # Report malformed record, discard results, continue polling
        print("Message deserialization failed {}".format(e))
        pass
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        print("Consumer stop, Leave group and commit final offsets")

consume()
