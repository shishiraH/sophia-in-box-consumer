from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroConsumer, AvroProducer
from confluent_kafka.avro.serializer import SerializerError
import os
import uuid
from consumer import StringAvroConsumer
from config import (
    ENVIRONMENT,
    RANGE_IPM_CONSUMER_BOOTSTRAP_BROKERS,
    RANGE_IPM_CONSUMER_SASL_USERNAME,
    RANGE_IPM_CONSUMER_SASL_PASSWORD,
    RANGE_IPM_CONSUMER_SCHEMA_REGISTRY_URL,
    # RANGE_IPM_CONSUMER_BASIC_AUTH_CREDENTIALS_SOURCE,
    # RANGE_IPM_CONSUMER_BASIC_AUTH_USER_INFO,
    RANGE_IPM_CONSUMER_GROUP_ID,
    RANGE_IPM_CONSUMER_AUTO_OFFSET_RESET,
    RANGE_IPM_CONSUMER_SSL_CA_LOCATION,
    DEBUG_KAFKA
)

config = {
    'bootstrap.servers': RANGE_IPM_CONSUMER_BOOTSTRAP_BROKERS,
    'client.id': 'giang_test',
    # 'sasl.mechanisms': 'PLAIN',
    # 'sasl.password': RANGE_IPM_CONSUMER_SASL_PASSWORD,
    # 'sasl.username': RANGE_IPM_CONSUMER_SASL_USERNAME,
    # 'security.protocol': 'SASL_SSL'
}


# https://confluent.cloud/environments/t613/clusters/lkc-ldoxz/consumerGroups/sophia_RANGE_IPM_CONSUMER_prod
def get_consumer():
    config['group.id'] = RANGE_IPM_CONSUMER_GROUP_ID
    config['auto.offset.reset'] = RANGE_IPM_CONSUMER_AUTO_OFFSET_RESET
    config['default.topic.config'] = {'auto.offset.reset': RANGE_IPM_CONSUMER_AUTO_OFFSET_RESET}
    config['schema.registry.url'] = RANGE_IPM_CONSUMER_SCHEMA_REGISTRY_URL
    # config['schema.registry.basic.auth.credentials.source'] = RANGE_IPM_CONSUMER_BASIC_AUTH_CREDENTIALS_SOURCE
    # config['schema.registry.basic.auth.user.info'] = RANGE_IPM_CONSUMER_BASIC_AUTH_USER_INFO
    # config['schema.registry.ssl.ca.location'] = RANGE_IPM_CONSUMER_SSL_CA_LOCATION
    config['api.version.request'] = True
    if DEBUG_KAFKA:
        config['debug'] = 'all'

    print(config)

    consumer = StringAvroConsumer(config)
    return consumer
