##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import numpy as np
import exputils as eu

def global_access_test(name, value):
    import exputils.data.logging as log

    assert log.contains(name)
    assert np.array_equal(log.get_values(name), value)


class TestObjClass():
    def __init__(self, val):
        self.val = val
        self.func = lambda x: x + val

def test_default_logger(tmp_path):

    import exputils.data.logging as log

    # default log
    log.add_value('prop1', 3.0)
    assert log.contains('prop1')
    global_access_test('prop1', [3.0])

    # new log - directly set
    log.log = eu.data.Logger()
    assert not log.contains('prop1')
    log.add_value('prop1', 4.0)
    assert log.contains('prop1')
    global_access_test('prop1', [4.0])

    # new log - setter function
    log.set_log(eu.data.Logger())
    assert not log.contains('prop1')
    log.add_value('prop1', 5.0)
    assert log.contains('prop1')
    global_access_test('prop1', [5.0])


def test_default_logger(tmp_path):

    import exputils.data.logging as log

    # reset log, in case it was used before
    log.reset()

    # make temporary folder for logs
    d = tmp_path / "logging"
    d.mkdir()

    # set different default logging
    log.set_directory(d)

    # write two logging entries
    log.add_value('prop1', 3.0)
    log.add_value('prop1', 4.0)
    log.add_value('prop2', 30.0)

    # write objects
    test_obj_1 = TestObjClass(1)
    test_obj_2 = TestObjClass(2)
    test_obj_3 = TestObjClass(3)

    log.add_object('objects', test_obj_1)
    log.add_object('objects', test_obj_2)

    log.add_single_object('test_obj_3', test_obj_3)

    # check logged data
    assert log.get_values('prop1')[0] == 3.0
    assert log.get_values('prop1')[1] == 4.0
    assert log.get_values('prop2')[0] == 30.0

    assert isinstance(log.get_values('objects')[0], TestObjClass) and log.get_values('objects')[0].val == 1
    assert isinstance(log.get_values('objects')[1], TestObjClass) and log.get_values('objects')[1].val == 2

    assert not log.contains('test_obj_3')

    # save the logging
    log.save()

    ###################
    # load the saved logging without object

    mylogger = eu.data.Logger()
    mylogger.load(directory=d)

    assert mylogger['prop1'][0] == 3.0
    assert mylogger['prop1'][1] == 4.0
    assert mylogger['prop2'][0] == 30.0

    assert 'objects' not in mylogger
    assert 'test_obj_3' not in mylogger

    ###################
    # load the saved logging with objects

    mylogger = eu.data.Logger()
    mylogger.load(directory=d, load_objects=True)

    assert mylogger['prop1'][0] == 3.0
    assert mylogger['prop1'][1] == 4.0
    assert mylogger['prop2'][0] == 30.0

    assert isinstance(mylogger['objects'][0], TestObjClass) and mylogger['objects'][0].val == 1
    assert isinstance(mylogger['objects'][1], TestObjClass) and mylogger['objects'][1].val == 2
    assert isinstance(mylogger['test_obj_3'], TestObjClass) and mylogger['test_obj_3'].val == 3