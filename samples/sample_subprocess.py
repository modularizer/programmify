import sys
import time

from programmify import SubprocessWidget


def sample(start, stop, interval=1):
    for i in range(start, stop):
        print(i)
        time.sleep(interval)


if __name__ == '__main__':
    if "--run" in sys.argv:
        start = int(sys.argv[1])
        stop = int(sys.argv[2])
        interval = int(sys.argv[3])
        sample(start, stop, interval)
    else:
        cmd = [sys.executable, __file__, '1000', '1200', '1', "--run"]
        SubprocessWidget.run(cmd=cmd)
