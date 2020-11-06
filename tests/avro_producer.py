from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from pytest import fixture


value_schema = avro.loads("""
        {
       "namespace": "my.test",
       "name": "value",
       "type": "record",
       "fields" : [
         {
           "name" : "name",
           "type" : "string"
         }
       ]
    }
""")

key_schema = avro.loads("""
    {
       "namespace": "my.test",
       "name": "key",
       "type": "record",
       "fields" : [
         {
           "name" : "name",
           "type" : "string"
         }
       ]
    }
""")


@fixture
def producer(config):
    producer = AvroProducer(
        dict(config),
        default_key_schema=key_schema,
        default_value_schema=value_schema)
    yield producer
