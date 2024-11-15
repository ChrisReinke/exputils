# Logging

Functions to log data for experiments.

All functions can be accessed under the module: ``exputils.data.logging``


## Usage 

Import the logging module and directly use its functions to log values or objects. 
It is not necessary to create a logging object.

Scalars and arrays will be logged as numpy arrays in the memory.

:warning: To write the logged values to disk it is necessary to call the [save](#exputils.data.logging.save) function.

__Example__:
    ```python
    # import the logging module as log
    import exputils.data.logging as log
    
    # use the log to log some scalars under the name 'val'
    for i in range(10):
        log.add_value('val', i)
    
    # save the log, only then will the log be written from memory to a file!
    log.save()
    ```


## Writting 

::: exputils.data.logging
    options:
        members:
            - add_value
            - add_scalar
            - add_histogram
            - add_object
            - add_single_object
            - save
            - clear
            - reset


## Reading

Values that were logged can also be accessed.
It is also possible to load a complete log from disk.
This can be used to continue experiment and add new values to an existing log.

::: exputils.data.logging
    options:
        members:
            - contains
            - items
            - get_item
            - get_values
            - get_objects
            - load
            - load_single_object


## Tensorboard

The log has the ability to log values in parallel to Tensorboard which can be used to visualize them while an experiment
is running.

::: exputils.data.logging
    options:
        members:
            - tensorboard
            - create_tensorboard
            - activate_tensorboard
            - deactivate_tensorboard
            - is_tensorboard_active


## Configuration 

To configure the default directory the logging is using.

::: exputils.data.logging
    options:
        members:
            - set_directory
            - get_directory 