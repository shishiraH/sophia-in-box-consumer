from uuid import uuid4 as uuid

from confluent_kafka import OFFSET_END
from confluent_kafka.avro import AvroConsumer
from pytest import fixture


@fixture
def consumer(config, topic):
    config = dict(config, **{
        'group.id': 'test_group_35',
    })
    consumer = AvroConsumer(config)

    # Subscribe to topics/partitions, and seek to end. Following that we need
    # to poll until the topics have actually been assigned.
    def on_assign(consumer, partitions):
        for p in partitions:
            p.offset = OFFSET_END
        consumer.assign(partitions)
    consumer.subscribe([topic], on_assign=on_assign)
    consumer.poll(10)

    yield consumer

    consumer.commit()
    consumer.close()
