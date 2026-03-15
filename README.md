# 🛡️ ApexHunter - Smart Threat Hunting Made Simple

[![Download ApexHunter](https://img.shields.io/badge/Download-ApexHunter-green?style=for-the-badge)](https://github.com/abubakerawad/ApexHunter/releases)

---

## 🔍 What is ApexHunter?

ApexHunter is a tool built to help security teams find threats faster. It runs playbooks written in simple YAML files. These playbooks guide the tool to scan and analyze forensic logs. It uses local machine learning models to make sense of data without needing an internet connection. This helps spot threats, link events, map to known attack techniques, and produce clear reports automatically. The tool works offline and stores its data using DuckDB for quick processing.

You do not need to be an expert in cybersecurity or coding to use it. ApexHunter is designed with simplicity in mind.

---

## 📋 Features at a Glance

- Runs automated playbooks for threat detection and investigation  
- Works with common forensic logs like EVTX files from Windows event logs  
- Uses local language models (Ollama) to understand and correlate data  
- Maps events to MITRE ATT&CK strategies for clear threat context  
- Saves data using DuckDB for fast searching and analysis  
- Creates detailed reports to help share findings with others  
- Offline-first approach means it does not send your data to the internet  
- Supports a range of cybersecurity and incident response workflows

---

## 💻 System Requirements

- **Operating System:** Windows 10 or later (64-bit recommended)  
- **Memory:** At least 8 GB RAM  
- **Storage:** Minimum 1 GB free disk space  
- **Processor:** Intel i5 or equivalent or better  
- **Additional Software:**  
  - Python 3.8 or higher installed and added to your system PATH  
  - Ollama local language model set up (instructions below)  

---

## 🚀 Getting Started: How to Download and Run ApexHunter

1. **Visit the download page**  
   Go to the ApexHunter releases page on GitHub here:  
   [Download ApexHunter](https://github.com/abubakerawad/ApexHunter/releases)  

2. **Find the latest version**  
   Look for the newest release at the top of the list. Releases are organized by date and version number (e.g., v1.0, v1.1).

3. **Download the Windows package**  
   Click on the file labeled for Windows, such as `ApexHunter-Setup.exe` or a ZIP file containing the program. Save it to your computer.

4. **Run the installer**  
   - If you downloaded an `.exe` file, double-click it to start the installer.  
   - Follow the on-screen instructions to complete installation.  

5. **Set up Python (if needed)**  
   If Python is not yet installed on your computer:  
   - Download Python from https://www.python.org/downloads/windows/  
   - Run the installer and make sure to tick the option "Add Python to PATH"  
   - After installation, restart your computer.  

6. **Install Ollama**  
   ApexHunter uses Ollama for its language models. To install Ollama on Windows:  
   - Visit https://ollama.com/install  
   - Follow the instructions for Windows to complete installation  
   - Once installed, open your command prompt and type `ollama --version` to verify it is working.  

7. **Run ApexHunter**  
   - Open the folder where you installed ApexHunter.  
   - Double-click the executable to start the application.  

8. **Load your forensic data**  
   - Use the interface to add EVTX or other log files for analysis.  
   - Select or write YAML playbooks to run on your data.  

9. **Review reports**  
   Once analysis finishes, ApexHunter will generate reports showing detected threats and their mappings.

---

## 🛠️ Using ApexHunter: Basic Workflow

- **Step 1: Prepare your logs**  
  Gather Windows event logs (`.evtx` files) or any supported forensic files you want to investigate.

- **Step 2: Choose a playbook**  
  Playbooks are scripts written in YAML that guide the threat hunting process. ApexHunter includes example playbooks with common tactics and detection rules.

- **Step 3: Run the playbook**  
  Load the log files and select a playbook in the ApexHunter interface. Click "Run" to start analysis.

- **Step 4: View results**  
  Check the output screen for correlated findings, mapped ATT&CK techniques, and summary statistics.

- **Step 5: Export report**  
  Use the export option to save a PDF or HTML report. Share this with your team or management as needed.

---

## 🔧 Configuration and Settings

ApexHunter allows you to customize several options to fit your needs:

- **Log input paths** – Choose where your logs come from and add multiple files.  
- **Playbook selection** – Browse built-in or add custom YAML playbooks.  
- **Language model settings** – Adjust how ApexHunter uses Ollama for analysis.  
- **Report format** – Pick between different report types and detail levels.  
- **Data storage** – Choose where DuckDB saves processed data for later use.  

Use the "Settings" menu inside the application to adjust these parameters.

---

## 📂 File Management

- ApexHunter supports `.evtx`, `.json`, `.csv`, and text-based forensic log formats.  
- Keep all input logs in easily accessible folders.  
- Playbooks must follow a strict YAML format. Example playbooks are included in the installation folder under `playbooks/`.

---

## ⚙️ Troubleshooting

- **ApexHunter does not start:**  
  Make sure you installed Python and Ollama properly. Check that ApexHunter’s files are not blocked by antivirus software.

- **Playbooks fail to run:**  
  Verify your YAML files have correct syntax. Use provided example playbooks to test.

- **No results after analysis:**  
  Confirm your log files contain relevant data. Try different or larger log sets.

- **Ollama errors:**  
  Check Ollama installation by running `ollama --version` in Command Prompt. Reinstall if necessary.

---

## 🧰 Useful Links

- [ApexHunter Releases](https://github.com/abubakerawad/ApexHunter/releases)  
- [Python for Windows](https://www.python.org/downloads/windows/)  
- [Ollama Installation](https://ollama.com/install)  
- [MITRE ATT&CK Framework](https://attack.mitre.org/)  

---

## 📝 About This Tool

ApexHunter is made to support security operations centers (SOC) and digital forensics teams. It bridges technical analysis with automated workflows. The tool aims to speed up investigations without relying on cloud services or internet access. It uses local machine resources and powerful data handling through DuckDB. This approach gives users full control over their sensitive data.