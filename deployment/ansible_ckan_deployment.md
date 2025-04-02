# **Step-by-Step Guide Automating CKAN Setup Using Ansible**

---

## **Step 1: Set Up Linux VM**

1. Update Ubuntu:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install required dependencies:

   ```bash
   sudo apt install -y ansible python3-pip git
   ```

---

## **Step 2: Set Up Ansible**

  Create an Ansible directory:

   ```bash
   mkdir -p ~/ansible-ckan
   cd ~/ansible-ckan
   ```

---

## **Step 3: Define Inventory and Variables**

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

## **Step 4: Create the Ansible Playbook**

1. Create a new playbook file:

   ```bash
   nano ckan_setup.yml
   ```

2. Paste the following playbook inside the file and save:  

   ```yaml

   ---
   - name: Install and Configure CKAN on Ubuntu 22.04
     hosts: ckan_servers
     become: yes
     vars_files:
       - group_vars/vault.yml
   
     tasks:
       - name: Update system packages
         apt:
           update_cache: yes
   
       - name: Install required dependencies
         apt:
           name:
             - python3-pip
             - libpq5
             - redis-server
             - nginx
             - supervisor
             - postgresql
             - openjdk-11-jdk
             - unzip
             - wget
           state: present
   
       - name: Start PostgreSQL (WSL / Remote)
         command: service postgresql start
         ignore_errors: yes
   
       - name: Create CKAN database user
         shell: |
           sudo -u postgres psql -c "CREATE ROLE {{ ckan_db_user }} WITH LOGIN PASSWORD '{{ ckan_db_password }}' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
         ignore_errors: yes
   
       - name: Create CKAN database
         shell: sudo -u postgres createdb -O {{ ckan_db_user }} {{ ckan_db_name }} -E utf-8
         ignore_errors: yes
   
       - name: Create datastore user
         shell: |
           sudo -u postgres psql -c "CREATE ROLE {{ datastore_user }} WITH LOGIN PASSWORD '{{ datastore_password }}' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
           sudo -u postgres psql -c "GRANT CONNECT ON DATABASE {{ ckan_db_name }} TO {{ datastore_user }};"
         ignore_errors: yes
   
       - name: Set permissions for CKAN directories
         file:
           path: /var/lib/ckan/default
           state: directory
           owner: www-data
           group: www-data
           mode: 0775
   
       - name: Download CKAN package
         get_url:
           url: "https://packaging.ckan.org/python-ckan_{{ ckan_version }}-jammy_amd64.deb"
           dest: "/tmp/python-ckan_{{ ckan_version }}-jammy_amd64.deb"
   
       - name: Install CKAN package
         command: dpkg -i /tmp/python-ckan_{{ ckan_version }}-jammy_amd64.deb
         ignore_errors: yes
   
       - name: Fix missing dependencies
         command: apt-get install --fix-broken -y
   
       - name: Fix permissions for webassets
         file:
           path: /var/lib/ckan/default/webassets
           state: directory
           owner: www-data
           group: www-data
           mode: 0775
   
       - name: Ensure CKAN configuration file is in place
         copy:
           src: /etc/ckan/default/ckan.ini
           dest: /etc/ckan/default/ckan.ini
           owner: www-data
           group: www-data
           mode: 0644
           remote_src: yes
   
       - name: Download and install Solr
         shell: |
           wget -O /tmp/solr.tgz https://dlcdn.apache.org/solr/solr/{{ solr_version }}/solr-{{ solr_version }}.tgz
           tar xzf /tmp/solr.tgz -C /opt/
         args:
           creates: "/opt/solr-{{ solr_version }}"
   
       - name: Start Solr
         shell: nohup /opt/solr-{{ solr_version }}/bin/solr start &
         ignore_errors: yes
   
       - name: Create Solr core for CKAN
         command: /opt/solr-{{ solr_version }}/bin/solr create -c ckan
         ignore_errors: yes
   
       - name: Start CKAN
         shell: nohup /usr/lib/ckan/default/bin/ckan -c /etc/ckan/default/ckan.ini run > /dev/null 2>&1 &
         args:
           executable: /bin/bash
         ignore_errors: yes
   ```

---

## **Step 5: Create CKAN Configuration File**

1. Create the CKAN configuration file:

   ```bash
   mkdir -p ~/ansible-ckan/templates
   nano ~/ansible-ckan/templates/ckan.ini.j2
   ```

2. Paste the following inside and save:

   ```ini
   [app:main]
   sqlalchemy.url = postgresql://{{ ckan_db_user }}:{{ ckan_db_password }}@localhost/{{ ckan_db_name }}
   ckan.site_url = http://localhost:5000
   solr_url = http://127.0.0.1:8983/solr/ckan
   ckan.plugins = stats text_view recline_view
   ckan.site_id = default
   ```

---

## **Step 6: Run the Ansible Playbook**

1. Navigate to your playbook directory:

   ```bash
   cd ~/ansible-ckan
   ```

2. Run the playbook:

   ```bash
   ansible-playbook -K -i inventory.ini ckan_local_setup.yml --ask-vault-pass
   ```

---

## **Step 7: Verify CKAN is running**

  Verify CKAN is running:

   ```bash
   curl http://localhost:5000
   ```

  Open CKAN in Browser:
  <http://localhost:5000>
  