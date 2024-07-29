# http_server

Script run http server with methods GET and HEAD.

## Installation

````bash
poetry install
````

## Runs

````bash
make run_server
poetry run python src/http_server/server.py
````

## Tests

````bash
make test
poetry run pytest tests/
````

## ApacheBench results
````bash
./ab -n 1000 -c 10 http://localhost:5431/
This is ApacheBench, Version 2.3 <$Revision: 1913912 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:
Server Hostname:        localhost
Server Port:            5431

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      10
Time taken for tests:   3.208 seconds
Complete requests:      1000
Failed requests:        0
Non-2xx responses:      1000
Total transferred:      31000 bytes
HTML transferred:       0 bytes
Requests per second:    311.70 [#/sec] (mean)
Time per request:       32.082 [ms] (mean)
Time per request:       3.208 [ms] (mean, across all concurrent requests)
Transfer rate:          9.44 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.5      0       2
Processing:     2   11   6.5     10      63
Waiting:        1   11   6.4      9      61
Total:          2   11   6.5     10      64

Percentage of the requests served within a certain time (ms)
  50%     10
  66%     13
  75%     15
  80%     15
  90%     17
  95%     18
  98%     24
  99%     44
 100%     64 (longest request)
````
