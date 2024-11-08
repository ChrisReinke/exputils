
The exputils package has several submodules that are organized according to functionality.
The submodules must not be imported individually.
After importing the `exputils` module all can be accessed through it.

List of submodules:

- `exputils`: [Basic functionality](#basic-functions) that contain the [`AttrDict`](#exputils.misc.attrdict.AttrDict) 
    to define experiment configurations and functions that help to use the configuration.
- `exputils.manage`: Functions to generate experiments from a configuration template and to execute them with support 
    for parallel execution. See the [Manage](manage.md) section for details.
- `exputils.data`: Functions that are data related, such as [Logging](logging.md) and [Loading](loading.md) of experiment data.
- `exputils.gui.jupyter`: Widgets and plotting functions to load and plot logged data in Jupyter notebook.
    See the [Visualization](visualization.md) section for details.
- `exputils.io`: Basic [IO](io.md) helper functions which are used by the exputils package.
    They are usually not needed to log or load data which is done with the functions under the `exputils.data` module. 
- `exputils.misc`: Various helper functions used by the exputils package. Not yet documented.

Note: As this is a one-person development project, not all functionality is documented yet. In question, please refer
directly to the source code or contact me.

## Basic Functions

::: exputils.misc.attrdict
    options:
        filters: ["AttrDict"]
        members:
            - AttrDict
            - combine_dicts

::: exputils.misc.misc
    options:
        members:
            - create_object_from_config
            - call_function_from_config
            - seed
            - update_status



## Default Variables
The package has a list of default variables located on the module level that mainly control the names of the generated 
directories. They can be adjusted if needed.

| Name	                            | Type 	  | Description  	                                                                                                                                                             | Default  	                           |
|----------------------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `DEFAULT_ODS_CONFIGURATION_FILE` | `str`   | Filename of the ODS configuration file for campaigns.                                                                                                                      | `'experiment_configurations.ods'`  |
| `DEFAULT_EXPERIMENTS_DIRECTORY`  | `str`	  | Name of the directory in the campaign directory under which experiment directories are created. 	                                                                          | `'experiments'`	                                    |
| `EXPERIMENT_DIRECTORY_TEMPLATE`  | `str`	  | Name template of experiment directories. Has to contain a placeholder for the ID. 	                                                                                        | `'experiment_{:06d}'`	                                    |
| `REPETITION_DIRECTORY_TEMPLATE`  | `str`   | Name template of repetition directories. Has to contain a placeholder for the ID.	                                                                                         | `'repetition_{:06d}'`	                                    |
| `DEFAULT_DATA_DIRECTORY`         | `str`	  | Name of the directory that is used to store the logs under each repetition.	                                                                                               | `'data'`	                                    |
| `REPETITION_DATA_KEY`            | `str`	  | Keyname of the element in the `AttrDict` returned by the [`load_experiment_data`][exputils.data.loading.load_experiment_data] function that holds all the repetition data. 	 | `'repetition_data'`	                                    |

To customize them they can be changed after the exputils package as been imported:
```python
import exputils as eu
# use a shorter form for experiment and repetition directories
eu.EXPERIMENT_DIRECTORY_TEMPLATE = 'exp_{:06d}' 
eu.REPETITION_DIRECTORY_TEMPLATE = 'rep_{:06d}'
```



