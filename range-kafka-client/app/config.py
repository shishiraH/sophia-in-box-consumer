ENVIRONMENT = 'dev'
# Kafka
# RANGE_IPM_CONSUMER_BOOTSXTRAP_BROKERS = 'pkc-4jyq4.ap-southeast-2.aws.confluent.cloud:9092'
RANGE_IPM_CONSUMER_BOOTSTRAP_BROKERS = 'broker:9092'
RANGE_IPM_CONSUMER_SASL_USERNAME = 'V6R54MOZVOR44QGV'
RANGE_IPM_CONSUMER_SASL_PASSWORD = 'bBDUZlwxGiI2p9TgJg7T7GtnJV1fFeW0N0rXdy5WtIWS9XRNN4fJKMGkngN6dVEA'
RANGE_IPM_CONSUMER_SCHEMA_REGISTRY_URL ='http://localhost:8081'
# RANGE_IPM_CONSUMER_SCHEMA_REGISTRY_URL = "https://schema-registry.sophia.int.ap-southeast-2.datasvcsdev.a-sharedinfra.net:8081"
# RANGE_IPM_CONSUMER_BASIC_AUTH_CREDENTIALS_SOURCE = os.getenv('RANGE_IPM_CONSUMER_BASIC_AUTH_CREDENTIALS_SOURCE', 'USER_INFO')
# RANGE_IPM_CONSUMER_BASIC_AUTH_USER_INFO = os.getenv('RANGE_IPM_CONSUMER_BASIC_AUTH_USER_INFO', RANGE_IPM_CONSUMER_SASL_USERNAME + ':' + RANGE_IPM_CONSUMER_SASL_PASSWORD)
RANGE_IPM_CONSUMER_GROUP_ID =  'rangingtool_ipm_consumer_grp' + '_' + ENVIRONMENT
RANGE_IPM_CONSUMER_AUTO_OFFSET_RESET = 'earliest'
RANGE_IPM_CONSUMER_SSL_CA_LOCATION = '/etc/ssl/certs/KmartCertROOT.cer'
MESSAGE_KEY_FIELD = 'MESSAGE_KEY'
CHOSEN_GROUP_TOPIC = 'test-1'


WAIT_TIME = 10
MAX_WAIT_TIMES = 5

DEBUG_KAFKA = True
