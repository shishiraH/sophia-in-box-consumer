These are instructions for installing prerequisites on Windows 7, running on-premises at Kmart.

1. Install Docker Toolbox

    Windows 7 can not run Docker for Windows, which provides a smooth developer experience. Instead you should install [Docker Toolbox], which runs a VM using `boot2docker`. It operates in a similar fashion, but requires more manual configuration.

    Before continuing, install [Docker Toolbox].

1. Proxy settings

    Docker needs to download images from Docker Hub. To do so, it will need to make HTTP(S) requests to `docker.io` - so you need to set up `boot2docker` to use the proxy server. It will need to know the address of the proxy server, and also the credentials to log in to it.

    It's best not to store your NTLM credentials in environment variables. Instead, use a local proxy server that you control, and get a _token_ for authentication. You should [set up `cntlm`][cntlm] on your Windows host, and configure `boot2docker` to use it as the proxy.

1. Port forwarding

    Docker containers have their own network interfaces (virtual Ethernet). When you start a container, you can map a port with syntax like `-p HOST_PORT:CONTAINER_PORT` - for example, `-p 8080:80`. With Docker for Linux, Mac and Windows, that would automatically open port `8080` on `localhost` and forward packets through to the service running in the container. But Docker Toolbox can't automatically open the port on your host. Therefore, you will need to manually forward the ports for services that you wish to use.

    For the Kafka broker and Schema Registry, you should add these port mappings to the NAT interface of your `boot2docker` VM:

     - `9092` -> `9092`
     - `29092` -> `29092`
     - `8081` -> `8081`

    You can do that in the VirtualBox machine settings. Scripting it from the command line should be possible, but is beyond the scope of this document.


For detailed instructions, see [_IT Software Development / Deployment strategies / Containers / Docker Toolbox_][dt-conf] in Confluence.


[Docker Toolbox]: https://docs.docker.com/toolbox/toolbox_install_windows/
[cntlm]: http://putuyoga.com/blog/configure-docker-toolbox-behind-ntlm-proxy
[dt-conf]: https://kmartonline.atlassian.net/wiki/spaces/ITSD/pages/399015998/Docker+Toolbox
