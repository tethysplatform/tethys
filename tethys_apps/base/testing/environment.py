from os import environ

TESTING_DB_FLAG = 'tethys-testing_'


def set_testing_environment(val):
    if val:
        environ['TETHYS_TESTING_IN_PROGRESS'] = 'true'
    else:
        environ['TETHYS_TESTING_IN_PROGRESS'] = ''
        del environ['TETHYS_TESTING_IN_PROGRESS']


def get_test_db_name(orig_name):
    if TESTING_DB_FLAG not in orig_name:
        test_db_name = '{0}{1}'.format(TESTING_DB_FLAG, orig_name)
    else:
        test_db_name = orig_name

    return test_db_name


def is_testing_environment():
    return environ.get('TETHYS_TESTING_IN_PROGRESS')
