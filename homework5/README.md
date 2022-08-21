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

python3 httpd.py -w 5

ab -n 50000 -c 100 -r http://localhost:8080/
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


Server Software:        OtusServer
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   21.890 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      8700000 bytes
HTML transferred:       1700000 bytes
Requests per second:    2284.19 [#/sec] (mean)
Time per request:       43.779 [ms] (mean)
Time per request:       0.438 [ms] (mean, across all concurrent requests)
Transfer rate:          388.13 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2  98.4      0   15369
Processing:     3   42  19.5     41    3573
Waiting:        3   42  19.5     41    3573
Total:          4   43 102.4     41   15411

Percentage of the requests served within a certain time (ms)
  50%     41
  66%     42
  75%     42
  80%     43
  90%     43
  95%     44
  98%     46
  99%     47
 100%  15411 (longest request)


