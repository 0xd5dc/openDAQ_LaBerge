import threading
import time
import datetime

__author__ = 'chex'


def stamp(delta=3):
    """

    :param delta: time, in seconds, to wait
    """
    threading.Timer(delta, stamp).start()
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print 'format 1: {0}, format 2: {1}'.format(ts, st)


def save_to_csv(file_name, csv_data):
    """


    :param csv_data: csv string e.g. "1,2,3,4"
    :param filename: e.g. "output"
    """
    with open('{0}.csv'.format(file_name), 'a') as csv_file:
        csv_file.write(csv_data)


def generate_sample_data(data_list):
    """

    :param data_list: input data list e.g. [1,2,3,4]
    :return: "1,2,3,4"
    """
    return ','.join([str(i) for i in data_list])


if __name__ == '__main__':
    stamp()
    save_to_csv('output', generate_sample_data([1, 2, 3, 3, 5]))