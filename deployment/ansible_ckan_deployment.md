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

## **Step 3: Set Up SSH for Ansible (Optional)**
If you're running Ansible locally, we’ll use localhost as the host.

**Create an inventory file**:
```bash
cd ~/ansible-ckan
nano inventory.ini
```
Paste this inside:
```
[ckan_servers]
localhost ansible_connection=local
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
    - name: Install and Configure CKAN on Ubuntu 22.04 in WSL
      hosts: localhost
      become: yes
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
    
        - name: Start PostgreSQL manually for WSL
          command: service postgresql start
          args:
            warn: false
          ignore_errors: yes
    
        - name: Create CKAN database user
          shell: |
            sudo -u postgres psql -c "CREATE ROLE ckan_default WITH LOGIN PASSWORD 'yourpassword' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
          ignore_errors: yes
    
        - name: Create CKAN database
          shell: sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
          ignore_errors: yes
    
        - name: Set up Datastore user
          shell: |
            sudo -u postgres psql -c "CREATE ROLE datastore_default WITH LOGIN PASSWORD 'yourpassword' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
            sudo -u postgres psql -c "GRANT CONNECT ON DATABASE ckan_default TO datastore_default;"
          ignore_errors: yes
    
        - name: Fix permissions for CKAN directories
          file:
            path: /var/lib/ckan/default
            state: directory
            owner: www-data
            group: www-data
            mode: 0775
    
        - name: Download CKAN package
          get_url:
            url: https://packaging.ckan.org/python-ckan_2.10-jammy_amd64.deb
            dest: /tmp/python-ckan_2.10-jammy_amd64.deb
    
        - name: Install CKAN package
          command: dpkg -i /tmp/python-ckan_2.10-jammy_amd64.deb
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
    
    
        - name: Download and Install Solr manually
          shell: |
            wget -O /tmp/solr.tgz https://dlcdn.apache.org/solr/solr/9.8.0/solr-9.8.0.tgz
            tar xzf /tmp/solr.tgz -C /opt/
          args:
            creates: /opt/solr-9.8.0
    
        - name: Ensure Solr service is running manually
          shell: |
            nohup /opt/solr-9.8.0/bin/solr start &
          ignore_errors: yes
    
        - name: Create Solr core for CKAN
          command: /opt/solr-9.8.0/bin/solr create -c ckan
          ignore_errors: yes
    
        - name: Restart CKAN manually for WSL
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
   sqlalchemy.url = postgresql://ckan_default:yourpassword@localhost/ckan_default
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
   ansible-playbook -K -i inventory.ini ckan_local_setup.yml
   ```
   It will ask for your sudo password to install software.

---

## **Step 7: Verify CKAN is running**

  Verify CKAN is running:
   ```bash
   curl http://localhost:5000
   ```
  Open CKAN in Browser:
  http://localhost:5000
  

