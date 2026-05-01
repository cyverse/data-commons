# CyVerse Data Commons

## CKAN

The folder [ckan](ckan) provides help with deploying CKAN. See [CKAN Deployment](ckan/README.md) for more information.

To run the script, use

```
 sudo ansible-playbook -i inventory.ini ansible_script.yml --ask-vault-pass
 ```
 from the `ckan` directory. This will prompt you for the vault password to access the secrets in `vault.yml`. Make sure to have your `inventory.ini` configured with the target server's IP address and credentials.

## Kando (CyVerse Data Commons Management Tool)

The folder [kando](kando) provides a **user-friendly interface using Gradio** to manage datasets in the **CyVerse Discovery Environment (DE)** and other cloud storage services. See [Kando Documentation](kando/README.md) for more information.
