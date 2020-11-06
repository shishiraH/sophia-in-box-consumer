#!/usr/bin/env bash

set -euo pipefail

echo `date` "Waiting for broker"
docker-compose exec broker \
  cub kafka-ready -b broker:9092 1 120 > /dev/null || \
  ( echo "Timed out waiting for broker"; exit 1 )

echo `date` "Waiting for Schema Registry"
docker-compose exec broker \
  cub sr-ready schema-registry 8081 120 > /dev/null || \
  ( echo "Timed out waiting for Schema Registry"; exit 1 )

echo `date` "Waiting for LTS API"
docker-compose exec lts-api \
  bash -c "for i in \$(seq 1 120); do curl --output /dev/null --silent --fail http://lts-api:8070 && exit 0; sleep 1; done; exit 1" || \
  ( echo "Timed out waiting for LTS API"; exit 1 )

echo `date` "Kafka stack is UP"
