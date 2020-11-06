FROM python:3.6
WORKDIR /usr/src/app
RUN apt-get update

RUN wget https://github.com/edenhill/librdkafka/archive/v1.2.0.tar.gz && tar xvzf v1.2.0.tar.gz && cd librdkafka-1.2.0/ && ./configure && make && make install && ldconfig

RUN pip install --upgrade pip
COPY ./range-kafka-client/requirements.txt .
RUN pip install -r requirements.txt

# ENV HTTP_PROXY="http://proxy.int.sharedsvc.a-sharedinfra.net:8080"
# ENV HTTPS_PROXY="https://proxy.int.sharedsvc.a-sharedinfra.net:8080"
# ENV NO_PROXY=".kaccess.net,.kaccess.com.au,.kmtltd.net.au,.compute.internal,.a-sharedinfra.net,s3.ap-southeast-2.amazonaws.com,dynamodb.ap-southeast-2.amazonaws.com,169.254.169.254,169.254.170.2,.ap-southeast-2.elb.amazonaws.com,.elb.ap-southeast-2.amazonaws.com,sqs.ap-southeast-2.amazonaws.com"
COPY ./range-kafka-client/ .

COPY range-kafka-client/certs/kmart-ca-bundle.pem /etc/ssl/certs/kmart-ca-bundle.pem
COPY range-kafka-client/certs/KmartCertROOT.cer /etc/ssl/certs/KmartCertROOT.cer

CMD [ "python", "./app/main.py" ]
