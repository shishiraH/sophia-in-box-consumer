import requests


def produce_schemas(port, count):
    data = '{"schema": "{\\"type\\": \\"string\\"}"}'
    headers = {
    'Content-Type': 'application/vnd.schemaregistry.v1+json',
    }

    print("Data:", data)
    for num in range(count):
        url = "http://localhost:{}/subjects/{}/versions".format(
            port,
            "KafkaTest-key-"+ str(num))
        print("URL:", url)
        response = requests.post(
            url,
            data=data,
            headers=headers)
        print("Status:{} Response:{0}",
            str(response.status_code), str(response.text))

if __name__ == '__main__':
    port = int(input("Enter port:"))
    count = int(input("Enter loop count:"))
    produce_schemas(port, count)
