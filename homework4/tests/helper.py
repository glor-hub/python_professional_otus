import functools
import logging

logging.basicConfig(filename=None,
                    format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception:
                    logging.exception(f'Test failed at case {c}')
                    raise

        return wrapper
    return decorator
