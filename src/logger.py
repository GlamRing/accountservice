import datetime


def log(string):
    line = "[{}] {}".format(datetime.datetime.now(), string)
    print(line)

    with open("bypass_utility.log", "a