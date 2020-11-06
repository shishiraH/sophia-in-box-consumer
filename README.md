# Sophia In-A-Box

This is a minimal version of the Sophia platform that you can run in your development environment. It is functionally similar to the cloud-based Sophia platform. Use it to run experiments and test data pipelines.

There are two main components:

- **Streaming**: a packaged version of Kafka and the schema registry. This uses [Confluent's Docker images][cp-docker-images] to mimic the Confluent Cloud.
- ~~**Everything else**: fake long-term storage buckets, analysis and compute services. This uses [LocalStack] to mimic our setup of AWS.~~ Not implemented yet.

Both run in [Docker].


## Prerequisites

General steps:
 1. Checkout [`sophia-connect-watcher`] and [`sophia-lts-api`] to the parent directory. I.e `sophia-connect-watcher` should be a sibling of `sophia-in-a-box`.
 1. Configure your HTTP proxy settings. Ensure you can reach https://docker.io - otherwise Docker won't be able to pull any images.
 ```
 # Linux AWS WorkSpace (using CNTLM)
 export HTTPS_PROXY=http://127.0.0.1:3128
 # Linux/Mac workstation:
 export HTTPS_PROXY=httpgw.core.kmtltd.net.au:8080
 # Windows:
 setx HTTPS_PROXY httpgw.core.kmtltd.net.au:8080
 ```
 1. Install [Docker] and [`docker-compose`]. Follow those links to find instructions for your system. On some systems, `docker-compose` is included in the base Docker install.
 1. Ensure you have enough RAM available to Docker - about 4GB.

Platform-specific instructions:
 - AWS Linux WorkSpaces: [prj-workspaces/aws-linux-workspace](https://git.kaccess.net/prj-workspaces/aws-linux-workspace)
 - On-premises Windows 7: [README-Windows7.md](README-Windows7.md)


## Running (using go.sh on Unix)

The `start` target will start all services, create required resources, and return when everything is ready.
```
./go.sh start
```

For more options run:
```
./go.sh -h
```


## Running (using docker-compose)

Create a local bucket for long-term storage:

To start, first create the target S3 bucket, and then start the other services:
```bash
# Start all services
docker-compose up -d

# Create long-term storage bucket
export AWS_AWS_DEFAULT_REGION=ap-southeast-2 AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar
aws --endpoint-url=http://localhost:4572 s3 mb s3://raw-test

# Restart Kafka Connect (since it needs the bucket to be there)
docker-compose restart connect

# Wait for key services to accept connections
./status.sh
```

To stop but preserve data (e.g. Kafka topics):
```
docker-compose stop
```

To stop and destroy data:
```
docker-compose down -v
```


## Interacting with Sophia In A Box

Services that mirror functionality provided by Sophia:

| Service                 | Host address     | Docker address\*       |
|-------------------------|------------------|------------------------|
| Bootstrap broker        | `localhost:9092` | `broker:9092`          |
| Schema registry         | `localhost:8081` | `schema-registry:8081` |
| Long-term storage API   | `localhost:8070` | `lts-api:8070`         |
| Long-term storage S3    | `localhost:4572` | `s3:4572`              |

Services which are not currently published by Sophia, but which could be if there was a need:

| Service          | Host address     | Docker address\*       |
|------------------|------------------|------------------------|
| Zookeeper        | `localhost:2181` | `zookeeper:2181`       |
| Connect          | `localhost:8083` | `connect:8083`         |
| Control Center   | `localhost:9021` | `control-center:9021`  |

Other services available in [`docker-compose.extras.yml`]

| Service          | Host address     | Docker address\*       |
|------------------|------------------|------------------------|
| KSQL Server      | `localhost:8088` | `ksql-server:8088`     |
| KSQL CLI         | -                | -                      |
| REST proxy       | `localhost:8082` | `rest-proxy:8082`      |

<small>\* Use the Docker addresses if you want to connect to the services from other containers.</small>

Diagnostic use cases:

- Access Confluent Control Center in your web browser at http://localhost:9021.

- Execute Kafka command line tools from inside a container. For example, to list available topics:

  ```
  docker-compose exec broker \
    kafka-topics --zookeeper zookeeper:2181 --list
  ```

- Alternatively, use the [`ccloud` CLI tool][ccloud]. When using `ccloud`, make sure you use the local configuration directory `./ccloud`, as shown below:

  ```
  ccloud -c ./ccloud topic list
  ```

- Execute KSQL queries.

  ```
  docker-compose -f docker-compose.yml -f docker-compose.extras.yml exec \
   ksql-cli ksql http://ksql-server:8088
  ```


[Docker]: https://docs.docker.com/install/
[`docker-compose`]: https://docs.docker.com/compose/install/
[cp-docker-images]: https://github.com/confluentinc/cp-docker-images
[LocalStack]: https://github.com/localstack/localstack
[ccloud]: https://docs.confluent.io/current/cloud/using/index.html#ccloud-install-cli
[`sophia-connect-watcher`]: https://git.kaccess.net/prj-sophia/sophia-connect-watcher
[`sophia-lts-api`]: https://git.kaccess.net/prj-sophia/sophia-lts-api
[`docker-compose.extras.yml`]: ./docker-compose.extras.yml


## Testing (using go.sh on Unix)

```
./go.sh start tests
```


## Testing (using docker-compose)

Ensure the stack is running, as described above. Then start a Docker container to run the tests.

```
docker-compose -f docker-compose.tests.yml build
docker-compose -f docker-compose.tests.yml run test-kafka
```

To use localstack with aws cli, you should set some environment variables. For more details, refer to the [localstack documentation].

```
command1.  export AWS_AWS_DEFAULT_REGION=ap-southeast-2 AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar
command2.  aws --endpoint-url=http://localhost:4572 s3 mb s3://raw-test
IF you get an error in command2  then
run the following
    aws configure
    type  foo  then enter
    type bar then enter
    type ap-southeast-2 then enter
    and enter
Now try command2 again

To view the topics use the following:
   aws --endpoint-url=http://localhost:4572 s3 ls s3://raw-test/topics/
```

[pipenv]: https://pipenv.readthedocs.io/en/latest/
[Python 3]: https://www.python.org/download/releases/3.0/
[localstack documentation]: https://github.com/localstack/awscli-local
