# Setup Guide

Step-by-step instructions to replicate the SOC lab with Wazuh SIEM and a local Ollama LLM.

## Prerequisites

- Windows 10 host machine
- Oracle VirtualBox installed
- Ubuntu Server 22.04 ISO
- At least 8GB RAM (4GB allocated to the VM)
- Both machines on the same LAN (bridged adapter)

## Step 1 - Set Up the Ubuntu VM in VirtualBox

1. Create a new VM in VirtualBox with the following settings:
   - OS: Ubuntu 64-bit
   - RAM: 4096 MB minimum
   - Storage: 20GB+
   - Network: Set adapter to **Bridged Adapter** (so the VM gets a real LAN IP)
2. Mount the Ubuntu Server 22.04 ISO and install the OS.
3. Note the VM's IP address after boot:
   ```bash
   ip a
   ```

## Step 2 - Install Wazuh Manager on Ubuntu

Follow the official Wazuh installation guide for the all-in-one deployment (Manager + Dashboard):

```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
sudo bash wazuh-install.sh -a
```

Once complete, access the Wazuh Dashboard at:
```
https://192.168.0.11
```

Default credentials are shown at the end of the install script output.

## Step 3 - Install Wazuh Agent on Windows

1. Download the Wazuh Windows Agent installer from:
   https://packages.wazuh.com/4.x/windows/wazuh-agent-4.7.0-1.msi
2. Run the installer and set the Manager IP to your Ubuntu VM IP (e.g., `192.168.0.11`).
3. Start the agent service via PowerShell (run as Administrator):
   ```powershell
   NET START WazuhSvc
   ```
4. Verify the agent appears in the Wazuh Dashboard under **Agents**.

## Step 4 - Configure File Integrity Monitoring (FIM)

On the Windows machine, open `ossec.conf` in Notepad with Administrator rights:

```
C:\Program Files (x86)\ossec-agent\ossec.conf
```

Add a directory to monitor inside the `<syscheck>` block:

```xml
<directories check_all="yes" realtime="yes">C:\Users\lenovo\TestFolder</directories>
```

Restart the Wazuh agent after saving:

```powershell
NET STOP WazuhSvc
NET START WazuhSvc
```

## Step 5 - Install Ollama on Windows and Expose over LAN

1. Download and install Ollama from https://ollama.com/download
2. Pull the Llama 3.1 8B model:
   ```powershell
   ollama pull llama3.1:8b
   ```
3. By default, Ollama only binds to localhost. To expose it over LAN, set the environment variable and restart:
   ```powershell
   $env:OLLAMA_HOST = "0.0.0.0:11434"
   ollama serve
   ```
4. Create an inbound firewall rule to allow the Ubuntu VM to reach port 11434:
   ```powershell
   New-NetFirewallRule -DisplayName "SOCAI Ollama Access" `
     -Direction Inbound `
     -Protocol TCP `
     -LocalPort 11434 `
     -Action Allow
   ```

## Step 6 - Verify Cross-Machine Connectivity

From Windows, confirm Ollama is running:
```powershell
curl http://127.0.0.1:11434/api/tags
```

From the Ubuntu VM, confirm LAN access to Ollama:
```bash
curl http://192.168.0.10:11434/api/tags
```

Both should return a JSON list of available models.

## Step 7 - Set Up the Python SOC-AI Engine on Ubuntu

Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv -y
python3 -m venv socai-env
source socai-env/bin/activate
pip install requests
```

Copy `socai.py` to the Ubuntu VM and run it:
```bash
python3 socai.py
```

The script will send a sample Wazuh alert to the Ollama API on Windows and print the LLM's structured SOC analysis.

## Step 8 - Test File Integrity Monitoring

1. Create a test folder and file on Windows:
   ```
   C:\Users\lenovo\TestFolder\testfile.txt
   ```
2. The Wazuh agent will detect the change and send an alert to the manager.
3. Check the Wazuh Dashboard under **Security Events** to see the FIM alert.
4. Run `socai.py` with the alert details to get an AI analysis of the event.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Wazuh Dashboard not loading | Check service status: `sudo systemctl status wazuh-dashboard` |
| Agent not showing in Dashboard | Verify Manager IP in agent config and restart the agent service |
| Ollama unreachable from Ubuntu | Check firewall rule and confirm `OLLAMA_HOST=0.0.0.0:11434` is set |
| pip install blocked | Use a virtual environment: `python3 -m venv env && source env/bin/activate` |
| FIM alerts not appearing | Confirm the directory path in ossec.conf and restart the agent |
