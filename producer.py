import argparse
import logging

import orjson
import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", choices=["beanstalkd", "redis"])
    parser.add_argument("-qh", "--queue-host", required=True)
    parser.add_argument("-qp", "--queue-port", type=int, required=True)
    parser.add_argument("-n", "--message-count", default=100000, type=int)
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    try:
        produce = globals()[f"produce_to_{args.queue}"]
    except KeyError:
        logger.warning(f"producer for {args.queue} is not implemented")
    else:
        produce(args)


def produce_to_beanstalkd(args: argparse.Namespace) -> None:
    import pystalk

    client = pystalk.BeanstalkClient(args.queue_host, args.queue_port)
    logger.info("inititalized client")
    message = orjson.dumps({"foo": "bar"})

    for _ in tqdm.tqdm(tqdm.trange(args.message_count)):
        client.put_job(message)
    logger.info(f"produced {args.message_count} messages, terminating")


if __name__ == "__main__":
    main(parse_args())
