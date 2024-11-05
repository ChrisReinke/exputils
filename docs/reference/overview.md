TODO:

### Default Variables
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



