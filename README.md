# hsa-hw-13-queues-comparison

Redis vs Beanstalkd queues comparison.

## Results

### beanstalkd

beanstalkd (binlog to outer volume)

```log
100%|██████████| 100000/100000 [01:21<00:00, 1224.52it/s]  # producer
100%|██████████| 100000/100000 [01:46<00:00, 942.10it/s]   # consumer
```

beanstalkd (no binlog) – 6-8 times faster!

```log
100%|██████████| 100000/100000 [00:10<00:00, 9251.05it/s]  # producer
100%|██████████| 100000/100000 [00:21<00:00, 4570.58it/s]  # consumer
```
