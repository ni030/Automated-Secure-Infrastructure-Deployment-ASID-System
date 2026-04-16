# 🛡️ Automated Secure Infrastructure Deployment System

A robust, centralized orchestration system designed to automate the deployment, security, and maintenance of server infrastructure. This project uses Python as a control plane to trigger Ansible playbooks, manage Dockerized applications, and enforce strict firewall and authentication protocols.

## 🎬 Demo Video

[![Real-Time SecOps Dashboard Demo](https://github.com/user-attachments/assets/24eedde2-d615-4f5b-984e-434de7f1f959)](https://youtu.be/LA6jahXmnsU)
*Click the image above to watch the full demonstration on YouTube.*

---

## ✨ Key Features

* **Infrastructure as Code (IaC):** Fully automated server provisioning and configuration using Ansible.
* **Containerized Workloads:** Seamless deployment and lifecycle management of Dockerized applications.
* **Intelligent Orchestration:** A centralized Python script that manages the deployment pipeline from end to end.
* **Self-Healing Mechanisms:** Automated monitoring that detects failed services or containers and restarts them without manual intervention.
* **Hardened Security Posture:** * Strict SSH key-based authentication (disabling password logins).
  * Automated Uncomplicated Firewall (UFW) configuration to lock down unauthorized ports.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your local control node:
* **Python 3.8+**
* **Ansible** (`sudo apt install ansible` or `brew install ansible`)
* SSH access to your target server(s) with a user that has `sudo` privileges.

---

## 🚀 Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/automated-secure-infra.git](https://github.com/yourusername/automated-secure-infra.git)
cd automated-secure-infra
```

**2. Set up the Python Virtual Environment**
It is recommended to use a virtual environment to isolate project dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Configure your Environment**

- Update the Ansible inventory file (inventory/hosts.ini) with your target server IP addresses.

- Ensure your SSH public key is added to the ~/.ssh/authorized_keys of your target servers.

- Modify the .env file (if applicable) with your specific environment variables.

---

**💻 Usage**
Once your environment is configured, you can trigger the entire deployment process via the Python orchestrator.

```bash
# Example command to run the deployment
python3 app.py --deploy all
```
_Note: Replace app.py with the actual name of your primary Python script._


**🔒 Security Considerations**

This system modifies core security components of the target servers. By default, the deployment will:

- Block all incoming ports except for SSH (22), HTTP (80), and HTTPS (443) via UFW.

- Disable PasswordAuthentication in the SSH daemon config.

Please ensure you have a persistent SSH key connection before running the full playbook, otherwise you may lock yourself out of the target machine.
