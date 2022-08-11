### Описание Web-сервера

### Архитектура
В основе реализации - Multi-threaded на N workers. На тестировании данная реализация показала 
хорошие результаты по скорости и отказоустойчивости. 

Воркеры реализованы на основе процессов с помощью модуля `multiprocessing`. 
На каждый запрос пользователя внутри выбранного процесса создается новый поток, 
в котором происходит обработка запроса и возвращается ответ.


### Запуск скрипта
```
python3 httpd.py -w=<workers count> -p=<port> -r=<document root>

```

### Тесты
```
python3 -m unittest httptest.py

```

### Нагрузочное тестирование 

```

python3 httpd.py -w 8

This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   56.388 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      49987
Total transferred:      5198648 bytes
HTML transferred:       0 bytes
Requests per second:    886.71 [#/sec] (mean)
Time per request:       112.776 [ms] (mean)
Time per request:       1.128 [ms] (mean, across all concurrent requests)
Transfer rate:          90.03 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    7  93.7      0    3156
Processing:     1   30 690.0     14   55360
Waiting:        1   24 452.4     13   27849
Total:          1   38 714.5     14   56384

Percentage of the requests served within a certain time (ms)
  50%     14
  66%     17
  75%     19
  80%     21
  90%     26
  95%     31
  98%     39
  99%     50
 100%  56384 (longest request)

