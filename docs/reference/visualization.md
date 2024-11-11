# Jupyter Visualization

Jupyter notebook can be used to visualize the logged data. 
For this purpose, several Jupyter widgets and plotting functions based on plotly and tabulate are provided.

All widgets and functions can be accessed under the module: ``exputils.gui.jupyter``

Please note that the current widgets only work with Jupyter Notebook <= 6.5 and are also not compatible with Jupyter Lab.

## General Widgets 

::: exputils.gui.jupyter.experiment_data_loader_widget
    options:
        filters: ["ExperimentDataLoaderWidget"]

::: exputils.gui.jupyter.experiment_data_plot_selection_widget
    options:
        filters: ["ExperimentDataPlotSelectionWidget"]

## Plotting Functions

::: exputils.gui.jupyter.plotly_meanstd_scatter
    options:
        members:
            - plotly_meanstd_scatter

::: exputils.gui.jupyter.plotly_box
    options:
        members:
            - plotly_box


::: exputils.gui.jupyter.plotly_meanstd_bar
    options:
        members:
            - plotly_meanstd_bar

::: exputils.gui.jupyter.tabulate_meanstd
    options:
        members:
            - tabulate_meanstd

::: exputils.gui.jupyter.tabulate_pairwise
    options:
        members:
            - tabulate_pairwise