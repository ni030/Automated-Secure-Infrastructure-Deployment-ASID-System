import subprocess

def run_command(cmd):
    print(f"\n>>> {cmd}\n")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("❌ Command failed")
    else:
        print("✅ Success")

def main():
    print("=== Automated Infra System ===")

    run_command("ansible-playbook -i hosts.ini playbooks/install_docker.yml")
    run_command("ansible-playbook -i hosts.ini playbooks/deploy_app.yml")
    run_command("ansible-playbook -i hosts.ini playbooks/security.yml")
    run_command("ansible-playbook -i hosts.ini playbooks/monitor.yml")

    print("\n🎯 Deployment Completed")

if __name__ == "__main__":
    main()