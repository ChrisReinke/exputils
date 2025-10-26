# Test the new ExperimentDataLoaderWidget implementation
import sys
import os
sys.path.insert(0, '/home/fuchs/data/study/projects/exputils')

import exputils as eu
import pandas as pd

# Create dummy data functions (similar to what was in the test notebook)
def dummy_load_descriptions(experiments_directory):
    """Dummy function to load experiment descriptions"""
    descriptions = {}
    for i in range(5):
        exp_id = f"exp_{i:03d}"
        descriptions[exp_id] = {
            'id': exp_id,
            'order': i,
            'is_load_data': True,
            'name': f'Experiment {i}',
            'short_name': f'Exp{i}',
            'description': f'Description for experiment {i}',
            'directory': f'/path/to/exp_{i:03d}',
            'repetition_ids': [0, 1, 2]
        }
    return descriptions

def dummy_load_data(experiment_descriptions):
    """Dummy function to load experiment data"""
    data = {}
    for exp_id in experiment_descriptions:
        if experiment_descriptions[exp_id]['is_load_data']:
            data[exp_id] = {
                'results': pd.DataFrame({
                    'metric': [1.0, 2.0, 3.0],
                    'value': [0.1, 0.2, 0.3]
                })
            }
    return data

# Event handlers
def on_experiment_data_loaded_handler(event):
    print(f"Data loaded event: {len(event.new)} experiments loaded")

def on_experiment_descriptions_updated_handler(event):
    print(f"Descriptions updated event: {len(event.new)} experiments")

print("Testing ExperimentDataLoaderWidget...")

# Test 1: Create the widget as requested in the user's example
try:
    exp_data_loader = eu.gui.dash.ExperimentDataLoaderWidget(
        load_experiment_descriptions_function=dummy_load_descriptions,
        load_experiment_data_function=dummy_load_data
    )

    # Register events
    exp_data_loader.on_experiment_data_loaded(on_experiment_data_loaded_handler)
    exp_data_loader.on_experiment_descriptions_updated(on_experiment_descriptions_updated_handler)

    print("✅ Widget created successfully!")
    print(f"Widget has {len(exp_data_loader.experiment_descriptions)} experiment descriptions")
    
    # Test loading data
    exp_data_loader.load_data()
    print(f"✅ Data loaded successfully! {len(exp_data_loader.experiment_data)} experiments loaded")
    
except Exception as e:
    print(f"❌ Error creating widget: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Test the component directly
try:
    component = eu.gui.dash.ExperimentDataLoaderComponent(
        load_experiment_descriptions_function=dummy_load_descriptions,
        load_experiment_data_function=dummy_load_data
    )
    print("✅ Component created successfully!")
    print(f"Component has {len(component.experiment_descriptions)} experiment descriptions")
    
except Exception as e:
    print(f"❌ Error creating component: {e}")
    import traceback
    traceback.print_exc()

print("Testing completed!")