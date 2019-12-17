``docker-optimizer`` allows collapsing multiple ``RUN`` layers into a
single one. This way, you can use the docker caching for development,
yet get fewer layers for the final container.

Installation
============

.. code:: sh

    pip install docker-optimizer

Usage
=====

Input ``Dockerfile.dev``:

.. code:: docker

    FROM python:3.8-slim-buster

    #============================================================================
    # Install requirements
    #============================================================================
    COPY requirements.txt /requirements.txt
    RUN pip install -r /requirements.txt

    #============================================================================
    # Update the package list
    #============================================================================
    RUN apt-get update -y

    #============================================================================
    # Install certbot
    #============================================================================
    RUN apt-get install -y curl && \
        curl -LO https://dl.eff.org/certbot-auto && \
        mv certbot-auto /usr/local/bin && \
        chown root /usr/local/bin/certbot-auto && \
        chmod 755 /usr/local/bin/certbot-auto && \
        certbot-auto --install-only -n

    #============================================================================
    # cleanup package list
    #============================================================================
    RUN rm -rf /var/lib/apt/lists/*

    COPY new-certificate* /usr/local/bin/

    USER 1000
    ENV LE_AUTO_SUDO=
    WORKDIR /usr/local/bin
    ENTRYPOINT ["python", "new-certificate.py"]

.. code:: sh

    docker-optimizer Dockerfile.dev Dockerfile

.. code:: docker

    # compiled by docker-optimizer
    # https://github.com/bmustiata/docker-optimizer
    from python:3.8-slim-buster
    copy requirements.txt /requirements.txt
    run pip install -r /requirements.txt && apt-get update -y && apt-get install -y curl &&     curl -LO https://dl.eff.org/certbot-auto &&     mv certbot-auto /usr/local/bin &&     chown root /usr/local/bin/certbot-auto &&     chmod 755 /usr/local/bin/certbot-auto &&     certbot-auto --install-only -n && rm -rf /var/lib/apt/lists/*
    copy new-certificate* /usr/local/bin/
    user 1000
    env 'LE_AUTO_SUDO' ''
    workdir /usr/local/bin
    entrypoint ['python', 'new-certificate.py']
