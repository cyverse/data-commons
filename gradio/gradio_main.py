import gradio as gr
import subprocess

def migrate_all_datasets(username, password, ckan_org):
    # This function will call your script to migrate all datasets
    result = subprocess.run(['python', 'migrate_all_datasets.py', username, password, ckan_org], capture_output=True, text=True)
    return result.stdout

def migrate_single_dataset(username, password, ckan_org, dataset_path):
    # This function will call your script to migrate a single dataset
    result = subprocess.run(['python', 'migrate_single_dataset.py', dataset_path, ckan_org, username, password], capture_output=True, text=True)
    return result.stdout

# Interface for migrating all datasets
all_datasets_interface = gr.Interface(
    fn=migrate_all_datasets,
    inputs=[
        gr.Textbox(label="CyVerse Username"),
        gr.Textbox(label="CyVerse Password", type="password"),
        gr.Textbox(label="CKAN Organization")
    ],
    outputs="text",
    title="Migrate All Datasets",
    description="Migrate all datasets from Discovery Environment to CKAN."
)

# Interface for migrating a single dataset
single_dataset_interface = gr.Interface(
    fn=migrate_single_dataset,
    inputs=[
        gr.Textbox(label="CyVerse Username"),
        gr.Textbox(label="CyVerse Password", type="password"),
        gr.Textbox(label="CKAN Organization"),
        gr.Textbox(label="Absolute Path to Dataset")
    ],
    outputs="text",
    title="Migrate Single Dataset",
    description="Migrate a single dataset from Discovery Environment to CKAN."
)

# Combine both interfaces in a single tabbed interface
app = gr.TabbedInterface(
    [all_datasets_interface, single_dataset_interface],
    tab_names=["Migrate All Datasets", "Migrate Single Dataset"]
)

# Launch the interface
app.launch()
