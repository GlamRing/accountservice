import datetime


def log(string):
    line = "[{}] {}".format(datetime.datetime.now(), string)
    print(line)
