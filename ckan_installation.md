# CKAN Installation Guide

This guide provides a comprehensive, step-by-step walkthrough to install CKAN (2.10 on Ubuntu 22.04), covering every command needed to set up CKAN, PostgreSQL, Solr, and all necessary dependencies.

### Prerequisites:
- Ubuntu 22.04 or later
- Root (sudo) access
- Internet connection to download packages
- CKAN will be installed and configured to run with the Nginx web server and Supervisor process manager.

### **1. Update System**
To start, update your Ubuntu system to ensure that all packages are up-to-date.

```bash
sudo apt update
```
This command fetches updates from the repositories to ensure that you’re working with the latest versions of packages and security patches.

### **2. Install Required Dependencies**
Next, install the required packages for CKAN, including the PostgreSQL client library (`libpq5`), Redis (used for caching), Nginx (web server), and Supervisor (for managing processes):

```bash
sudo apt install -y libpq5 redis-server nginx supervisor
```

This command installs:
- `libpq5` - The PostgreSQL client library.
- `redis-server` - Redis, used for caching.
- `nginx` - Web server.
- `supervisor` - Process manager to ensure CKAN and related services stay running.

### **3. Download the CKAN Package**
Download the CKAN `.deb` package for Ubuntu 22.04 (Jammy) from the CKAN packaging repository:

```bash
wget https://packaging.ckan.org/python-ckan_2.10-jammy_amd64.deb
```

### **4. Install the CKAN Package**
Now, install CKAN using the downloaded `.deb` file:

```bash
sudo dpkg -i python-ckan_2.10-jammy_amd64.deb
```
This installs CKAN along with all necessary dependencies.

### **5. Install PostgreSQL**
CKAN requires a PostgreSQL database for data storage. Install PostgreSQL using the following command:

```bash
sudo apt install -y postgresql
```

### **6. List Databases in PostgreSQL**
To confirm that PostgreSQL is installed correctly, you can list the available databases:

```bash
sudo -u postgres psql -l
```
This will show a list of databases in PostgreSQL. Ensure that the `postgres` database is listed.

### **7. Create CKAN Database User**
Create a new PostgreSQL user for CKAN. This user will be used to manage the CKAN database:

```bash
sudo -u postgres createuser -S -D -R -P ckan_default
```
You will be prompted to enter a password for the `ckan_default` user. Make sure to remember this password, as you’ll need it for configuring CKAN.

### **8. Create CKAN Database**
Now, create the CKAN database and assign the user you just created (`ckan_default`) as the owner:

```bash
sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
```
This creates a new database called `ckan_default` with the correct encoding (`UTF-8`).

### **9. Install Java (Required for Solr)**
CKAN also requires Java for certain background services. Install OpenJDK 11:

```bash
sudo apt-get install openjdk-11-jdk
```

### **10. Download and Install Solr (for Search Functionality)**
CKAN uses Solr for full-text search. Install Solr by downloading it and using the installation script:

1. **Download Solr**:
   ```bash
   wget https://dlcdn.apache.org/solr/solr/9.7.0/solr-9.7.0.tgz
   ```

2. **Extract and Install Solr**:
   Extract the Solr archive and run the installation script:
   ```bash
   tar xzf solr-9.7.0.tgz solr-9.7.0/bin/install_solr_service.sh --strip-components=2
   sudo bash ./install_solr_service.sh solr-9.7.0.tgz
   ```

3. **Check Solr Service Status**:
   Verify that Solr is running correctly:
   ```bash
   sudo service solr status
   ```

### **11. Create a Solr Core for CKAN**
CKAN requires a specific Solr core (`ckan`) to store and manage indexed data. Create this core using Solr’s `bin/solr` script:

```bash
sudo -u solr /opt/solr/bin/solr create -c ckan
```

### **12. Download Solr Configuration Files**
Download the `managed-schema` file for CKAN to configure Solr:

```bash
sudo -u solr wget -O /var/solr/data/ckan/conf/managed-schema
```

### **13. Restart Solr**
After configuring Solr, restart it to apply the changes:

```bash
sudo service solr restart
```

### **14. Set Up CKAN’s Writable Directory**
CKAN requires a writable directory to store its temporary files. Create this directory, set appropriate ownership and permissions:

```bash
sudo mkdir -p /var/lib/ckan/default
sudo chown www-data /var/lib/ckan/default
sudo chmod u+rwx /var/lib/ckan/default
```

### **15. Configure CKAN**
Next, edit the CKAN configuration file (`ckan.ini`), which contains the settings for your CKAN instance, such as database connection and Solr URL.

```bash
nano /etc/ckan/default/ckan.ini
```

Here, make sure to update:
- `sqlalchemy.url` for PostgreSQL (`postgresql://ckan_default:password@localhost/ckan_default`).
- `solr_url` to point to your Solr instance (e.g., `http://localhost:8983/solr/ckan`).
- Other settings like site URL, email, etc., depending on your environment.

### **16. Test Database Connection**
Before proceeding, ensure that CKAN can connect to the PostgreSQL database:

```bash
psql -U ckan_default -d ckan_default -h localhost
```

You should be able to access the CKAN database from the command line. If you encounter an issue, verify that your `ckan.ini` configuration is correct.

### **17. Reload Supervisor and CKAN Services**
After making changes to the CKAN configuration, reload Supervisor and verify that CKAN services are running:

```bash
sudo supervisorctl reload
sudo supervisorctl status
```

### **18. Restart Nginx**
Restart the Nginx service to ensure that any changes to the configuration are applied:

```bash
sudo service nginx restart
```

### **19. Activate CKAN Environment**
Activate the CKAN environment, which is required to run CKAN’s management commands:

```bash
. /usr/lib/ckan/default/bin/activate
```

### **20. Add a CKAN Admin User**
Finally, create an administrator account for CKAN using the following command:

```bash
sudo -i
cd /usr/lib/ckan/default/src/ckan
ckan -c /etc/ckan/default/ckan.ini sysadmin add <your_username>
```
Replace `<your_username>` with your desired admin username. This will create the admin user with full privileges to manage CKAN.

---

### **Final Verification**

Once these steps are completed, CKAN should be fully installed and accessible through your web browser (usually `http://localhost` or the server's IP address).

You should be able to log in with the admin credentials you created and begin managing datasets and users.

---

### Troubleshooting

If you encounter issues:
- **PostgreSQL connection errors**: Double-check the PostgreSQL user and database settings in `ckan.ini`.
- **Solr issues**: Ensure Solr is running and properly configured for CKAN, including the `managed-schema`.
- **Service failures**: Use `sudo supervisorctl status` and `sudo service <service-name> status` to diagnose issues with CKAN or other services.
