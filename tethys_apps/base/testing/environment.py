from os import environ, unsetenv


def set_testing_environment(val):
    if val:
        environ['TETHYS_TESTING_IN_PROGRESS'] = 'true'
    else:
        environ['TETHYS_TESTING_IN_PROGRESS'] = ''
        del environ['TETHYS_TESTING_IN_PROGRESS']
        unsetenv('TETHYS_TESTING_IN_PROGRESS')


def is_testing_environment():
    return environ.get('TETHYS_TESTING_IN_PROGRESS')