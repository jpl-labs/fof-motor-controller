FROM resin/rpi-raspbian:jessie

RUN apt-get update && apt-get install -y \
	python3 \
	python3-dev \
	python3-pip \
	pigpio \
	python3-pigpio \
	--no-install-recommends && \
	rm -rf /var/lib/apt/lists/*

run pip3 install autobahn[asyncio]

copy / /fof/

WORKDIR /fof/

RUN pip3 install .

CMD python3 -m motor_controller
