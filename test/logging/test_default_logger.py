from exputils.logging import log
import exputils

def test_default_logger(tmp_path):

    # make temporary folder for logs
    d = tmp_path / "logging"
    d.mkdir()

    # set different default logging
    log.directory = d

    # write two logging entries
    log.add_value('prop1', 3.0)
    log.add_value('prop1', 4.0)

    log.add_value('prop2', 30.0)

    # check logged data
    assert log['prop1'][0] == 3.0
    assert log['prop1'][1] == 4.0
    assert log['prop2'][0] == 30.0

    # save the logging
    log.save()


    ###################
    # load the saved logging

    mylogger = exputils.logging.Logger()
    mylogger.load(directory=d)

    assert mylogger['prop1'][0] == 3.0
    assert mylogger['prop1'][1] == 4.0
    assert mylogger['prop2'][0] == 30.0