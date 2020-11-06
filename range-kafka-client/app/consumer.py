from confluent_kafka.avro import CachedSchemaRegistryClient, MessageSerializer
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka import Consumer


class StringAvroConsumer(Consumer):
    """
    Kafka Consumer client which does avro schema decoding of messages.
    Handles message deserialization.

    Constructor takes below parameters

    :param dict config: Config parameters containing url for schema registry (``schema.registry.url``)
                        and the standard Kafka client configuration (``bootstrap.servers`` et.al)
    :param schema reader_key_schema: a reader schema for the message key
    :param schema reader_value_schema: a reader schema for the message value
    :raises ValueError: For invalid configurations
    """

    def __init__(self, config, schema_registry=None, reader_key_schema=None, reader_value_schema=None):

        sr_conf = {key.replace("schema.registry.", ""): value
                   for key, value in config.items() if key.startswith("schema.registry")}

        if sr_conf.get("basic.auth.credentials.source") == 'SASL_INHERIT':
            sr_conf['sasl.mechanisms'] = config.get('sasl.mechanisms', '')
            sr_conf['sasl.username'] = config.get('sasl.username', '')
            sr_conf['sasl.password'] = config.get('sasl.password', '')

        ap_conf = {key: value
                   for key, value in config.items() if not key.startswith("schema.registry")}

        if schema_registry is None:
            schema_registry = CachedSchemaRegistryClient(sr_conf)
        elif sr_conf.get("url", None) is not None:
            raise ValueError("Cannot pass schema_registry along with schema.registry.url config")

        super(StringAvroConsumer, self).__init__(ap_conf)
        self._serializer = MessageSerializer(schema_registry, reader_key_schema, reader_value_schema)

    def poll(self, timeout=None):
        """
        This is an overriden method from confluent_kafka.Consumer class. This handles message
        deserialization using avro schema

        :param float timeout: Poll timeout in seconds (default: indefinite)
        :returns: message object with deserialized key and value as dict objects
        :rtype: Message
        """
        if timeout is None:
            timeout = -1
        message = super(StringAvroConsumer, self).poll()
        if message is None:
            return None
        print('consumer py message is not none')
        if not message.error():
            try:
                if message.value() is not None:
                    decoded_value = self._serializer.decode_message(message.value(), is_key=False)
                    print('IPM consumer | decoded_value',decoded_value,'message.value',message.value())
                    message.set_value(decoded_value)
            except SerializerError as e:
                raise SerializerError("Message deserialization failed for message at {} [{}] offset {}: {}".format(
                    message.topic(),
                    message.partition(),
                    message.offset(),
                    e))
        return message
