# CKAN Deployment

## 1. `deployment/ansible_script.yml`

- **Purpose**: Provides an **Ansible playbook** to deploy a new instance of CKAN.
- **Features**:
  - Automates installation and configuration of CKAN and its dependencies.
  - Can be used to deploy a CKAN instance on a cloud VM or on-premise server.
  - Highly customizable to match different deployment environments.

## 2. `deployment/ansible_ckan_deployment.md`

- **Purpose**: Provides **documentation** and step-by-step instructions for using the provided Ansible script.
- **Details**:
  - Describes prerequisites (Ansible installation, target machine setup).
  - Explains how to run the playbook and verify the deployed CKAN instance.


community.postgresql

## Custom Template Overrides

CKAN UI customizations live in `ckan/templates/` and follow CKAN's template inheritance structure. The Ansible playbook copies these to `/etc/ckan/default/custom_templates/` on the server and configures `extra_template_paths` in `ckan.ini`.

- **To add a customization**: Create the override file under `ckan/templates/` matching CKAN's directory structure (e.g., `package/search.html`) and use `{% ckan_extends %}` to inherit the base template. Rerun the playbook.
- **To undo a customization**: Delete the override file from `ckan/templates/` and rerun the playbook. CKAN falls back to its default template automatically.

Current overrides:
- `templates/package/search.html` — Adds DE date sort options (Date Created/Modified in Discovery Environment) to the dataset search dropdown.