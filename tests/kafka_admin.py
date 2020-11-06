from confluent_kafka.admin import AdminClient, NewTopic
from pytest import fixture


@fixture
def admin_client(config):
    admin_client = AdminClient({
        'bootstrap.servers': config['bootstrap.servers'],
    })
    yield admin_client
