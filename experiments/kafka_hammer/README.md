Stress test Kafka. Useful when experimenting with infrastructure.

```
PIPENV_VENV_IN_PROJECT=1 pipenv sync
pipenv run ./kafka_hammer.py -s <schema_registry_url> [-s ...] [-b <broker_address>] [--dynamic-schemas]
```

Options:

 - `-s`: Specify a schema registry URL. You can specify multiple SRs.
 - `-d`: Generate unique schemas to POST to the SRs, to force a write. Note that this will create a lot of schemas.
 - `-b`: Specify a broker. You can specify up to one broker. If you don't specify one, pub/sub jobs won't run.

You can specify multiple schema registries. Brokers are optional; if they are omitted, only the schema registry will be hammered.

If you want to pipe to a file and view on the console at the same time, you need to disable stdout buffering in Python and use tee:

```
pipenv run python -u \
    ./kafka_hammer.py -s <schema_registry_url> [-s ...] -b <broker_address> \
    | tee output.csv
```

You can also plot the results using gnuplot:

```
yum install gnuplot
gnuplot -e "inputfile='output.csv'" -p kafka_hammer.gnu 2>&1 \
    | grep -Ev "warning: Skipping|Warning: empty"
```

## Authentication and SSL

You can provide additional parameters for the Kafka client and SR by setting environment variables. For example:

```bash
export KAFKA_SASL_MECHANISMS=PLAIN
export KAFKA_SECURITY_PROTOCOL=SASL_SSL
export KAFKA_SSL_CA_LOCATION=`pwd`/ca-bundle.pem
export KAFKA_SASL_USERNAME=...
export KAFKA_SASL_PASSWORD=...
export SR_SCHEMA_REGISTRY_SSL_CA_LOCATIOn=`pwd`/ca-bundle.pem
pipenv run python -u ./kafka_hammer.py [etcetera]
```

The CA bundle should contain the full certificate chain. An easy way to create it is to concatenate your special CA cert with the OS bundle. Or just find an existing bundle in another project ;)
