#!/usr/bin/env python
import argparse
import csv
from copy import deepcopy
from datetime import datetime
import json
import logging
import os
import random
import re
import requests
import sys
import threading
import time

from confluent_kafka import OFFSET_END
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer, AvroConsumer

log = logging.getLogger('kafka_hammer')


TOPIC_PREFIX = 'sophia.hammer'


def configure_logging(level):
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
    )


def run(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--broker')
    parser.add_argument(
        '-s', '--schema-registry-url', action='append', default=[])
    parser.add_argument(
        '-p', '--period', type=float, default=0.2)
    parser.add_argument(
        '-r', '--report-period', type=float, default=1.0)
    parser.add_argument(
        '-d', '--dynamic-schemas', default=False, action='store_true')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0)
    args = parser.parse_args(argv)
    if args.verbose >= 2:
        configure_logging('DEBUG')
    elif args.verbose >= 1:
        configure_logging('INFO')
    else:
        configure_logging('WARNING')
    log.info("Starting with %s", args)

    csv_writer = csv.writer(sys.stdout)
    runner = Runner(args.report_period, csv_writer)


    for schema_registry_url in args.schema_registry_url:
        name = re.sub(r'https?://', '', schema_registry_url)
        name = re.sub(r'\W', '-', name)

        if args.broker:
            runner.add_job(AvroProducerJob(
                args.period, 'k-pub-%s' % name,
                args.broker, schema_registry_url))
            runner.add_job(CacheBustingAvroProducerJob(
                args.period, 'k-pub-no-cache-%s' % name,
                args.broker, schema_registry_url))

            runner.add_job(AvroConsumerJob(
                args.period, 'k-sub-%s' % name,
                args.broker, schema_registry_url))

        runner.add_job(SchemaRegistryIsUpJob(
            args.period, 'sr-is-up-%s' % name,
            schema_registry_url))
        runner.add_job(SchemaPostJob(
            args.period, 'sr-post-static-%s' % name,
            schema_registry_url))
        if args.dynamic_schemas:
            runner.add_job(UniqueSchemaPostJob(
                args.period, 'sr-post-unique-%s' % name,
                schema_registry_url))
        else:
            runner.add_job(NullJob(
                args.period, 'sr-null-%s' % name))
        runner.add_job(SchemaGetJob(
            args.period, 'sr-get-%s' % name,
            schema_registry_url))

    runner.run()


class Runner:
    def __init__(self, report_period, writer):
        self.jobs = []
        self.report_period = report_period
        self.writer = writer

    def add_job(self, job):
        self.jobs.append(job)

    def run(self):
        log.info("Running %d jobs", len(self.jobs))
        for job in self.jobs:
            job.prepare()
        headers = self.get_headers(self.jobs)
        self.writer.writerow(headers)
        for job in self.jobs:
            job.start()
        try:
            scheduler = Scheduler(self.report_period)
            while True:
                scheduler.wait()
                row = self.get_row(self.jobs)
                self.writer.writerow(row)
        except KeyboardInterrupt:
            log.debug("Received term signal")
            self.stop()

    def get_headers(self, jobs):
        headers = ['time']
        for job in jobs:
            headers.append("OK-%s" % job.name)
            headers.append("BAD-%s" % job.name)
        return headers

    def get_row(self, jobs):
        data = [job.take_datum() for job in self.jobs]
        row = [datetime.now().isoformat()]
        for datum in data:
            row.append(datum.good_count)
            row.append(datum.bad_count)
        return row

    def stop(self):
        stop_condition = threading.Condition()
        with stop_condition:
            for job in self.jobs:
                job.stop(stop_condition)
            log.debug("Waiting for jobs to stop")
            stop_condition.wait_for(
                lambda: all(job.state == 'STOPPED' for job in self.jobs),
                timeout=10)
            for job in self.jobs:
                job.shutdown()
        log.debug("Joining threads")
        for job in self.jobs:
            job.join(0)


class Scheduler:
    def __init__(self, period):
        self.period = period
        self.next_scheduled_time = time.time() + self.period

    def wait(self):
        now = time.time()
        while self.next_scheduled_time > now:
            time_to_wait = max(0, self.next_scheduled_time - now)
            time.sleep(time_to_wait)
            now = time.time()
        self.next_scheduled_time = now + self.period


class Job(threading.Thread):
    def __init__(self, period, name):
        super().__init__()
        self.name = name
        self.period = period
        self.stop_condition = None
        self.state = 'PENDING'
        self.datum = Datum()
        self.datum_lock = threading.Lock()

    def run(self):
        log.info("Starting job '%s'", self.name)
        self.state = 'RUNNING'
        scheduler = Scheduler(self.period)
        while not self.stop_condition:
            try:
                self.step()
            except Exception as e:
                log.debug("Failed to step job '%s': %s", self.name, e)
                self.update_datum(Datum(bad_count=1))
            scheduler.wait()
        self.state = 'STOPPED'
        with self.stop_condition:
            log.debug("Job '%s' has stopped", self.name)
            self.stop_condition.notify_all()

    def stop(self, stop_condition):
        log.info("Stopping job '%s'", self.name)
        self.stop_condition = stop_condition

    def take_datum(self):
        with self.datum_lock:
            datum = self.datum
            self.datum = Datum()
        return datum

    def update_datum(self, datum):
        with self.datum_lock:
            self.datum += datum

    def prepare(self):
        pass

    def step(self):
        raise NotImplemented

    def shutdown(self):
        pass


class NullJob(Job):
    def step(self):
        pass


SCHEMA_TEMPLATE = {
   "namespace": TOPIC_PREFIX,
   "name": "hammer",
   "type": "record",
   "fields": [
        {
            "name": "name",
            "type": "string"
        }
   ]
}


def get_schema_def():
    schema_def = deepcopy(SCHEMA_TEMPLATE)
    schema_def['namespace'] = "%s.static" % TOPIC_PREFIX
    schema_def['name'] = 'static'
    return json.dumps(schema_def)


def create_unique_schema_def():
    schema_def = deepcopy(SCHEMA_TEMPLATE)
    schema_def['namespace'] = "%s.dynamic" % TOPIC_PREFIX
    schema_def['name'] = 'dynamic_%s' % random.randint(0, 1000000000)
    return json.dumps(schema_def)


def snake_to_dotted(snake_name):
    dotted = snake_name.replace('_', '.')
    dotted = dotted.lower()
    return dotted


def remove_prefix(name, prefix):
    if not name.startswith(prefix):
        raise ValueError("Name does not start with specified prefix")
    return name[len(prefix):]


def get_dotted_config_from_environment(prefix):
    return {
        snake_to_dotted(remove_prefix(k, prefix)): v
        for k, v in os.environ.items()
        if k.startswith(prefix)
    }


def get_kafka_config_from_environment():
    return get_dotted_config_from_environment('KAFKA_')


def get_sr_config_from_environment():
    return get_dotted_config_from_environment('SR_')


class AvroProducerFacade:
    def __init__(
            self, name, emit_datum, broker, schema_registry_url):
        self.name = name
        self.emit_datum = emit_datum
        schema = avro.loads(get_schema_def())
        self.producer = AvroProducer({
            'bootstrap.servers': broker,
            'schema.registry.url': schema_registry_url,
            **get_sr_config_from_environment(),
            **get_kafka_config_from_environment(),
        }, default_key_schema=schema, default_value_schema=schema)

    def delivery_callback(self, err, msg):
        if err:
            log.debug("Failed to send from '%s': %s", self.name, err)
            datum = Datum(bad_count=1)
        else:
            datum = Datum(good_count=1)
        self.emit_datum(datum)

    def produce(self, topic, poll_wait=0):
        value = {'name': 'foo'}
        self.producer.produce(
            topic=topic, callback=self.delivery_callback,
            key=value, value=value)
        self.producer.poll(poll_wait)

    def close(self):
        self.producer.flush()


class AvroProducerJob(Job):
    def __init__(
            self, period, name, broker, schema_registry_url):
        super().__init__(period, name)
        self.broker = broker
        self.schema_registry_url = schema_registry_url

    def prepare(self):
        self.producer = AvroProducerFacade(
            self.name, self.update_datum,
            self.broker, self.schema_registry_url)

    def step(self):
        self.producer.produce('%s.static' % TOPIC_PREFIX, poll_wait=0)

    def shutdown(self):
        self.producer.close()


class CacheBustingAvroProducerJob(Job):
    def __init__(
            self, period, name, broker, schema_registry_url):
        super().__init__(period, name)
        self.broker = broker
        self.schema_registry_url = schema_registry_url

    def step(self):
        producer = AvroProducerFacade(
            self.name, self.update_datum,
            self.broker, self.schema_registry_url)
        try:
            producer.produce('%s.static' % TOPIC_PREFIX, poll_wait=20)
        finally:
            producer.close()


class AvroConsumerFacade:
    def __init__(
            self, name, emit_datum, broker,
            schema_registry_url, topic):
        self.name = name
        self.emit_datum = emit_datum
        self.consumer = AvroConsumer({
            'bootstrap.servers': broker,
            'group.id': name,
            'schema.registry.url': schema_registry_url,
            **get_sr_config_from_environment(),
            **get_kafka_config_from_environment(),
        })

        # Subscribe to topics/partitions, and seek to end. Following that we need
        # to poll until the topics have actually been assigned.
        def on_assign(consumer, partitions):
            for p in partitions:
                p.offset = OFFSET_END
            self.consumer.assign(partitions)
        self.consumer.subscribe([topic], on_assign=on_assign)
        self.consumer.poll(10)

    def consume_one(self, poll_wait=0):
        consumed_message = self.consumer.poll(poll_wait)
        if consumed_message is not None:
            self.emit_datum(Datum(good_count=1))
        else:
            self.emit_datum(Datum(bad_count=1))

    def close(self):
        self.consumer.commit()
        self.consumer.close()


class AvroConsumerJob(Job):
    def __init__(
            self, period, name, broker, schema_registry_url):
        super().__init__(period, name)
        self.broker = broker
        self.schema_registry_url = schema_registry_url

    def prepare(self):
        self.consumer = AvroConsumerFacade(
            self.name, self.update_datum,
            self.broker, self.schema_registry_url,
            '%s.static' % TOPIC_PREFIX)

    def step(self):
        self.consumer.consume_one(poll_wait=0)

    def shutdown(self):
        self.consumer.close()


class CacheBustingAvroConsumerJob(Job):
    def __init__(
            self, period, name, broker, schema_registry_url):
        super().__init__(period, name)
        self.broker = broker
        self.schema_registry_url = schema_registry_url

    def step(self):
        consumer = AvroConsumerFacade(
            self.name, self.update_datum,
            self.broker, self.schema_registry_url,
            '%s.static' % TOPIC_PREFIX)
        try:
            consumer.consume_one(poll_wait=5)
        finally:
            consumer.close()


def sr_requests_options(sr_config):
    return {
        'verify': sr_config.get('schema.registry.ssl.ca.location', ''),
        'proxies': {
            'http': sr_config.get('proxy', ''),
            'https': sr_config.get('proxy', ''),
        }
    }


class SchemaRegistryIsUpJob(Job):
    def __init__(self, period, name, schema_registry_url):
        super().__init__(period, name)
        self.schema_registry_url = schema_registry_url

    def step(self):
        headers = {
            'Accept': 'application/vnd.schemaregistry.v1+json',
        }
        url = "{}/subjects".format(self.schema_registry_url)
        sr_config = get_sr_config_from_environment()
        conn_options = sr_requests_options(sr_config)
        r = requests.get(url, headers=headers, timeout=5, **conn_options)
        if r.status_code != 200:
            log.warning(
                "Failed to contact registry: %s", r.text.replace('\n', ''))
            self.update_datum(Datum(bad_count=1))
            return
        self.update_datum(Datum(good_count=1))


class SchemaPostJob(Job):
    def __init__(self, period, name, schema_registry_url):
        super().__init__(period, name)
        self.schema_registry_url = schema_registry_url

    def step(self):
        data = json.dumps({'schema': get_schema_def()})
        headers = {
            'Content-Type': 'application/vnd.schemaregistry.v1+json',
        }
        url = "{}/subjects/{}/versions".format(
            self.schema_registry_url, '%s.static' % TOPIC_PREFIX)
        sr_config = get_sr_config_from_environment()
        conn_options = sr_requests_options(sr_config)
        r = requests.post(
            url, data=data, headers=headers, timeout=5, **conn_options)
        if r.status_code != 200:
            log.warning("Failed to post schema: %s", r.text.replace('\n', ''))
            self.update_datum(Datum(bad_count=1))
            return
        self.update_datum(Datum(good_count=1))


class UniqueSchemaPostJob(Job):
    def __init__(self, period, name, schema_registry_url):
        super().__init__(period, name)
        self.schema_registry_url = schema_registry_url

    def step(self):
        data = json.dumps({'schema': create_unique_schema_def()})
        headers = {
            'Content-Type': 'application/vnd.schemaregistry.v1+json',
        }
        url = "{}/subjects/{}/versions".format(
            self.schema_registry_url, '%s.dynamic' % TOPIC_PREFIX)
        sr_config = get_sr_config_from_environment()
        conn_options = sr_requests_options(sr_config)
        r = requests.post(
            url, data=data, headers=headers, timeout=5, **conn_options)
        if r.status_code != 200:
            log.warning("Failed to post schema: %s", r.text.replace('\n', ''))
            self.update_datum(Datum(bad_count=1))
            return
        self.update_datum(Datum(good_count=1))


class SchemaGetJob(Job):
    def __init__(self, period, name, schema_registry_url):
        super().__init__(period, name)
        self.schema_registry_url = schema_registry_url

    def step(self):
        headers = {
            'Accept': 'application/vnd.schemaregistry.v1+json',
        }
        url = "{}/subjects/{}/versions".format(
            self.schema_registry_url, '%s.static' % TOPIC_PREFIX)
        sr_config = get_sr_config_from_environment()
        conn_options = sr_requests_options(sr_config)
        r = requests.get(url, headers=headers, timeout=5, **conn_options)
        if r.status_code != 200:
            log.warning("Failed to get schema: %s", r.text.replace('\n', ''))
            self.update_datum(Datum(bad_count=1))
            return
        self.update_datum(Datum(good_count=1))


class Datum:
    __slots__ = ['good_count', 'bad_count']

    def __init__(self, good_count=0, bad_count=0):
        self.good_count = good_count
        self.bad_count = bad_count

    def __add__(self, other):
        return Datum(
            self.good_count + other.good_count,
            self.bad_count + other.bad_count)

    def __str__(self):
        return "+%d-%d" % (self.good_count, self.bad_count)


if __name__ == '__main__':
    run(sys.argv[1:])
