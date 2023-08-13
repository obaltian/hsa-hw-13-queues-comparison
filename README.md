# hsa-hw-13-queues-comparison

Redis vs Beanstalkd queues comparison.

## Results

### beanstalkd

```sh
rm queuedata/beanstalkd/*
docker-compose -f docker-compose-beanstalkd.yml up --exit-code-from=consumer
```

#### beanstalkd (binlog to outer volume), n=1000

```log
hsa-hw-13-queues-comparison-consumer-1  | 2023-08-13 11:31:50,416.416 INFO consumer - consume_from_beanstalkd: inititalized client
hsa-hw-13-queues-comparison-producer-1  | 2023-08-13 11:31:50,507.507 INFO producer - produce_to_beanstalkd: inititalized client
hsa-hw-13-queues-comparison-producer-1  | 2023-08-13 11:31:51,533.533 INFO producer - produce_to_beanstalkd: produced 1000 messages, terminating
hsa-hw-13-queues-comparison-consumer-1  | 2023-08-13 11:31:51,798.798 INFO consumer - consume_from_beanstalkd: consumed 1000 messages, terminating
```

- producer: 1s
- consumer: 1.4s

#### beanstalkd (no binlog), n=1000 – 6-8 times faster

```log
hsa-hw-13-queues-comparison-producer-1  | 2023-08-13 11:34:26,662.662 INFO producer - produce_to_beanstalkd: inititalized client
hsa-hw-13-queues-comparison-consumer-1  | 2023-08-13 11:34:26,723.723 INFO consumer - consume_from_beanstalkd: inititalized client
hsa-hw-13-queues-comparison-producer-1  | 2023-08-13 11:34:26,942.942 INFO producer - produce_to_beanstalkd: produced 1000 messages, terminating
hsa-hw-13-queues-comparison-consumer-1  | 2023-08-13 11:34:27,134.134 INFO consumer - consume_from_beanstalkd: consumed 1000 messages, terminating
```

- producer: 0.3s
- consumer: 0.4s

### Redis (RDB)  (saving dump.rdb to disk each second)

```sh
rm queuedata/redis-rdb/*
docker-compose -f docker-compose-redis-rdb.yml up > redis-rdb.log
```

#### redis (save .rdb each second, job results are discarded immediately (as binstalkd does)), n=1000

```log
hsa-hw-13-queues-comparison-queue-1     | 1:C 13 Aug 2023 11:06:57.532 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[...]
hsa-hw-13-queues-comparison-consumer-1  | 11:06:58 default: consumer.consumer_handler(17) (908f849e-0c73-4b8b-a135-65ba741a43ae)
hsa-hw-13-queues-comparison-producer-1 exited with code 0
[...]
hsa-hw-13-queues-comparison-consumer-1  | 11:07:21 Worker rq:worker:6cab5d02d5db45cabcaf84a072910e42: idle for 5 seconds, quitting
```

- producer: <1s
- consumer: 23 - 5 (timeout) ≈ 18s

Worker is so slow because `rq` forks a new process for each job, and it takes time to fork a process.
Let's try it without forking (`--worker-class=rq.worker.SimpleWorker`):

```log
hsa-hw-13-queues-comparison-queue-1     | 1:C 13 Aug 2023 11:41:46.411 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[...]
hsa-hw-13-queues-comparison-consumer-1  | 11:41:48 default: consumer.consumer_handler(77) (f9065c00-cd7c-4c78-91c0-c14cf640e9c1)
hsa-hw-13-queues-comparison-producer-1 exited with code 0
[...]
hsa-hw-13-queues-comparison-consumer-1  | 11:41:56 Worker rq:worker:5254fd7c89b8453c87c363e9a8efbfa1: idle for 5 seconds, quitting
```

- producer: 1.6s
- consumer: 9.6s - 5s (timeout) ≈ 4.6s

### Redis (AOF)

```sh
rm queuedata/redis-aof/*
docker-compose -f docker-compose-redis-aof.yml up > redis-aof.log
```

#### redis (AOF, job results are discarded immediately (as binstalkd does)), n=1000

```log
hsa-hw-13-queues-comparison-queue-1     | 1:C 13 Aug 2023 11:48:04.261 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[...]
hsa-hw-13-queues-comparison-consumer-1  | 11:48:06 Result discarded immediately
hsa-hw-13-queues-comparison-producer-1 exited with code 0
[...]
hsa-hw-13-queues-comparison-consumer-1  | 11:48:17 Worker rq:worker:0fed9912ba7c4cc6a2b2848afaf39cac: idle for 5 seconds, quitting
```

- producer: 2s
- consumer: 12.5 - 5 (timeout) ≈ 7.7s

## Conclusion

Being compared with single-thread producer and consumer (n=1000), beanstalkd seems to be the fastest one (as expected):

| Queue                   | Producer time, s | Consumer time, s |
| ----------------------- | ---------------- | ---------------- |
| Beanstalkd              | ≈1               | ≈1.4             |
| Redis (RDB, --save 1 1) | ≈1.6             | ≈4.6             |
| Redis (AOF)             | ≈2               | ≈7.7             |

Of course, the comparison is not ideal because `rq` library additionally stores function name and other metadata in queue.
However, I tried to test beanstalkd with more huge messages including function names and it was still much faster than Redis.
