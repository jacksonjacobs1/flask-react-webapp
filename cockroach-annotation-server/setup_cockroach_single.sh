#!/usr/bin/bash

docker network create -d bridge roachnet

docker volume create roach1



docker run -d --name=roach1 --hostname=roach1 --net=roachnet -p 26257:26257 -p 8080:8080 -v "roach1:/cockroach/cockroach-data" cockroachdb/cockroach:v23.2.5 start   --disable-max-offset-check --max-offset=5000ms --advertise-addr=roach1:26357   --http-addr=roach1:8080   --listen-addr=roach1:26357   --sql-addr=roach1:26257   --insecure   --join=roach1:26357,roach2:26357,roach3:26357 

docker exec -it roach1 ./cockroach --host=roach1:26357 init --insecure
docker exec -it roach1 ./cockroach sql --host=roach1:26257 --insecure
