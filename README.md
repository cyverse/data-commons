# CyVerse Data Commons

## CKAN

### Docker Configuration

#### 13. Dockerfile

- **Purpose**: Defines the **Docker configuration** for the project.
- **Details**:
  - Uses **Python 3.11 slim** as the base image.
  - **Copies only the `.py` files** to the container for a smaller image size.
  - Installs dependencies from `requirements.txt` and **exposes port 7860** for the Gradio UI.

---

### Deployment

#### 14. `deployment/ansible_script.yml`

- **Purpose**: Provides an **Ansible playbook** to deploy a new instance of CKAN.
- **Features**:
  - Automates installation and configuration of CKAN and its dependencies.
  - Can be used to deploy a CKAN instance on a cloud VM or on-premise server.
  - Highly customizable to match different deployment environments.

#### 15. `deployment/ansible_ckan_deployment.md`

- **Purpose**: Provides **documentation** and step-by-step instructions for using the provided Ansible script.
- **Details**:
  - Describes prerequisites (Ansible installation, target machine setup).
  - Explains how to run the playbook and verify the deployed CKAN instance.

---

## Kando (CyVerse Data Commons Management Tool)

The folder [kando](kando) provides a **user-friendly interface using Gradio** to manage datasets in the **CyVerse Discovery Environment (DE)** and other cloud storage services. See [Kando Documentation](kando/README.md) for more information.
