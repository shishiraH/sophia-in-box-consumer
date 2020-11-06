import random
import time
from uuid import uuid4 as uuid

from confluent_kafka import (
    avro,
    KafkaError,
    KafkaException,
    OFFSET_END,
    TopicPartition,
)
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroConsumer, AvroProducer
from confluent_kafka.avro.serializer import SerializerError
from pytest import fixture

from .kafka_admin import admin_client
from .avro_consumer import consumer
from .avro_producer import producer


@fixture
def config():
    yield {
        'bootstrap.servers': 'broker:9092',
        'schema.registry.url': 'http://schema-registry:8081',
    }


@fixture
def topic(admin_client):
    topic_name = 'sophia_in_a_box_test_topic'
    futures = admin_client.create_topics([NewTopic(topic_name, 1, 1)])
    try:
        futures[topic_name].result()
    except KafkaException as e:
        error = e.args[0]
        if error and error.code() == KafkaError.TOPIC_ALREADY_EXISTS:
            pass
    yield topic_name


def test_producer_should_be_able_to_publish_to_local_sophia_stack(
        topic, producer, consumer):
    test_message = {"name": str(random.randint(1, 1000))}
    test_key = {"name": "Key2"}
    producer.produce(topic=topic, value=test_message, key=test_key)
    producer.flush()
    consumed_message = consumer.poll(1)
    assert consumed_message.value() == test_message
