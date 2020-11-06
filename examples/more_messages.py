from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

import random



value_schema_str = """
{
   "namespace": "tech.demo",
   "name": "value",
   "type": "record",
   "fields" : [
     {
       "name" : "name",
       "type" : "string"
     },
     {
       "name" : "sequence",
       "type" : "string",
       "default": "null"
     }
   ]
}
"""

key_schema_str = """
{
   "namespace": "tech.demo",
   "name": "key",
   "type": "record",
   "fields" : [
     {
       "name" : "name",
       "type" : "string"
     }
   ]
}
"""

def message(value):
    return {
      "name": "data-" + str(random.randint(1, 10)),
      "sequence": " value-" + str(value)
      }

def delivery_callback(err, msg):
    if err:
        print('%% Message failed delivery: %s\n' % err)
    else:
        print('%% Message delivered to %s [%d] @ %o\n' %
              (msg.topic(), msg.partition(), msg.offset()))

def produce_message(count):
  value_schema = avro.loads(value_schema_str)
  key_schema = avro.loads(key_schema_str)
  key = {"name": "Key2"}

  avroProducer = AvroProducer({
      'bootstrap.servers': 'localhost:9092',
      'schema.registry.url': 'http://localhost:8081'
      }, default_key_schema=key_schema, default_value_schema=value_schema)

  for value in range (count):
    avroProducer.produce(topic='demo', value=message(value), key=key, callback=delivery_callback)
    avroProducer.flush()

if __name__ == '__main__':
    count = int(input("Enter number: "))
    produce_message(count)
