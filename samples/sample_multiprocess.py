import time

from programmify import MultiprocessWidget


def sample(start, stop, interval=1):
    for i in range(start, stop):
        print(i)
        time.sleep(interval)


if __name__ == '__main__':
    # wrapper(sample, 1000, 1200, 1)
    MultiprocessWidget.run(target=sample, args=(1000, 1005, 1))
