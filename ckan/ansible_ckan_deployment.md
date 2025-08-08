# Step-by-Step Guide Automating CKAN Setup Using Ansible

---

## Step 1: Set Up Linux VM

1. Update Ubuntu:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

1. Install required dependencies:

   ```bash
   sudo apt install -y ansible python3-pip git
   ```

---

## Step 2: Set Up Ansible

  Create an Ansible directory:

   ```bash
   mkdir -p ~/ansible-ckan
   cd ~/ansible-ckan
   ```

---

## Step 3: Define Inventory and Variables

### 3.1 Create Inventory File

```bash
nano inventory.ini
```

### For Local Testing

```ini
[ckan_servers]
localhost ansible_connection=local
```

### For Remote Deployment

```ini
[ckan_servers]
ckan-server ansible_host=YOUR_SERVER_IP ansible_user=YOUR_SSH_USER
```

---

### 3.2 Create Group Variables

Create a `group_vars` directory:

```bash
mkdir -p group_vars
```

### Define deployment variables

```bash
nano group_vars/ckan_servers.yml
```

Content:

```yaml
ckan_db_user: ckan_default
datastore_user: datastore_default
ckan_db_name: ckan_default

ckan_db_password: "{{ vault_ckan_db_password }}"
datastore_password: "{{ vault_datastore_password }}"
ckan_version: "2.10"
solr_version: "9.8.0"
```

---

### 3.3 Create Vault for Secrets

```bash
ansible-vault create group_vars/vault.yml
```

Add:

```yaml
vault_ckan_db_password: "your_ckan_password"
vault_datastore_password: "your_datastore_password"
```

---

## Step 4: Create CKAN Configuration File

1. Create the CKAN configuration file:

   ```bash
   mkdir -p ~/ansible-ckan/templates
   nano ~/ansible-ckan/templates/ckan.ini.j2
   ```

1. Paste the following inside and save:

   ```ini
   [app:main]
   sqlalchemy.url = postgresql://{{ ckan_db_user }}:{{ ckan_db_password }}@localhost/{{ ckan_db_name }}
   ckan.site_url = http://localhost:5000
   solr_url = http://127.0.0.1:8983/solr/ckan
   ckan.plugins = stats text_view recline_view
   ckan.site_id = default
   ```

---

## Step 5: Run the Ansible Playbook

1. Navigate to your playbook directory:

   ```bash
   cd ~/ansible-ckan
   ```

1. Run the playbook:

   ```bash
   ansible-playbook -i inventory.ini ansible_script.yml --ask-vault-pass
   ```

---

## Step 6: Verify CKAN is running

  Verify CKAN is running:

   ```bash
   curl http://localhost:5000
   ```

  Open CKAN in Browser:
  <http://localhost:5000>
