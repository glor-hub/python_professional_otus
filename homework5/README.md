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
Document Length:        35 bytes

Concurrency Level:      100
Time taken for tests:   22.273 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      8750000 bytes
HTML transferred:       1750000 bytes
Requests per second:    2244.90 [#/sec] (mean)
Time per request:       44.545 [ms] (mean)
Time per request:       0.445 [ms] (mean, across all concurrent requests)
Transfer rate:          383.65 [Kbytes/sec] received
  50%     44
  66%     44
  75%     45
  80%     45
  90%     46
  95%     48
  98%     50
  99%     50
 100%     52 (longest request)

