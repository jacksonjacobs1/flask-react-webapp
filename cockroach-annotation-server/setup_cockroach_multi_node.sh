




#---s1
export s1=170.140.138.87
export s2=170.140.138.63
export s3=170.140.138.73

docker volume create roach1
docker run -d --name=roach1 --hostname=roach1 -p 26357:26357 -p 9091:9091 -p26257:26257 -v "roach1:/cockroach/cockroach-data" cockroachdb/cockroach:v23.2.5 start   --advertise-addr=${s1}:26357   --http-addr=roach1:9091   --listen-addr=roach1:26357   --sql-addr=roach1:26257   --insecure   --join=${s1}:26357,${s2}:26357,${s3}:26357

#---s2
export s1=170.140.138.87
export s2=170.140.138.63
export s3=170.140.138.73

docker volume create roach2
docker run -d --name=roach2 --hostname=roach2 -p 26357:26357 -p 9091:9091 -p26257:26257 -v "roach2:/cockroach/cockroach-data" cockroachdb/cockroach:v23.2.5 start   --advertise-addr=${s2}:26357   --http-addr=roach2:9091   --listen-addr=roach2:26357   --sql-addr=roach2:26257   --insecure   --join=${s1}:26357,${s2}:26357,${s3}:26357


#---s3
export s1=170.140.138.87
export s2=170.140.138.63
export s3=170.140.138.73

docker volume create roach3
docker run -d --name=roach3 --hostname=roach3 -p 26357:26357 -p 9091:9091 -p26257:26257 -v "roach3:/cockroach/cockroach-data" cockroachdb/cockroach:v23.2.5 start   --advertise-addr=${s3}:26357   --http-addr=roach3:9091   --listen-addr=roach3:26357   --sql-addr=roach3:26257   --insecure   --join=${s1}:26357,${s2}:26357,${s3}:26357


docker exec -it roach1 ./cockroach --host=roach1:26357 init --insecure
docker exec -it roach1 ./cockroach sql --host=roach1:26257 --insecure




#laptop 
export s1=170.140.138.87
export s2=170.140.138.63
export s3=170.140.138.73
export s4=170.140.138.73

docker volume create roach4
docker run -d --name=roach4 --hostname=roach4 -p 26357:26357 -p 9091:9091 -p26257:26257 -v "roach4:/cockroach/cockroach-data" cockroachdb/cockroach:v23.2.5 start   --advertise-addr=${s4}:26357   --http-addr=roach4:9091   --listen-addr=roach4:26357   --sql-addr=roach4:26257   --insecure   --join=${s1}:26357,${s2}:26357,${s3}:26357

#---
#can do things like this to reduce the replicas and encourage more indexes

ALTER TABLE test1.public.annotations CONFIGURE ZONE USING
    num_replicas = 1,
    range_min_bytes = 5242880,
    range_max_bytes = 5242880;