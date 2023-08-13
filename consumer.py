import argparse
import logging

import tqdm

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", choices=["beanstalkd"])
    parser.add_argument("-qh", "--queue-host", required=True)
    parser.add_argument("-qp", "--queue-port", type=int, required=True)
    parser.add_argument("-n", "--message-count", default=100000, type=int)
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    try:
        consume = globals()[f"consume_from_{args.queue}"]
    except KeyError:
        logger.warning(f"consumer for {args.queue} is not implemented")
    else:
        consume(args)


def consume_from_beanstalkd(args: argparse.Namespace) -> None:
    import pystalk

    client = pystalk.BeanstalkClient(args.queue_host, args.queue_port)
    logger.info("inititalized client")

    for _ in tqdm.tqdm(tqdm.trange(args.message_count)):
        job = client.reserve_job()
        consumer_handler(int(job.job_data))
        client.delete_job(job.job_id)
    logger.info(f"consumed {args.message_count} messages, terminating")


def consumer_handler(number: int) -> int:
    return number


if __name__ == "__main__":
    main(parse_args())
