# CC Indicators

This repository provides tools and reproducible workflows to analyze historical atmospheric and oceanic climate indicators, with a focus on Pacific Ocean regions.

The project is structured around Jupyter notebooks that:

- Retrieve and preprocess historical climate datasets
- Compute climate indicators
- Generate figures and summary matrices
- Document methodologies in a transparent and reproducible way

All analyses are published through a Jupyter Book to ensure clarity, traceability, and reproducibility.

🔗 Project documentation:  
https://lauracagigal.github.io/CC_indicators/intro  

🔗 Summary matrix of results:  
https://lauracagigal.github.io/CC_indicators/extra/matrix_cc/index.html  

The repository is designed for research applications in climate variability assessment, ocean–atmosphere interaction studies, and regional climate diagnostics.


# ⚙️ Installation

This project can be run in two ways:

---

### **Option 1** — Recommended: GitHub Codespaces (Fully Configured Environment)

The repository includes a Docker-based development container with a stable and reproducible environment.

#### Steps

1. Go to the repository on GitHub.
2. Click **Code** → **Codespaces**.
3. Create a new Codespace.
4. Wait for the container to build (first time only).
5. Open the notebooks and start working.

No local installation is required.  
All dependencies are automatically installed through the provided Docker configuration.

**This is the most reproducible and recommended option.**


### **Option 2** — Local Installation (VS Code + Docker)

This option runs the exact same Docker environment locally using VS Code Dev Containers.

---

#### Steps

1. Install Required Software <br>

    - **Docker Desktop**  
  https://www.docker.com/products/docker-desktop/

    - **Visual Studio Code**  
        https://code.visualstudio.com/

   Open VS Code  
    - Go to **Extensions** → Install the extension: **Dev Containers** (by Microsoft)

2. Clone the Repository

    Open a terminal and run:

    ```bash
    git clone https://github.com/lauracagigal/CC_indicators.git
    cd CC_indicators
    ```
3. Open the Project in VS Code

4. Reopen in Container

    VS Code will detect the .devcontainer configuration automatically. You will see a popup asking to reopen in Container so you have to click ir.
    If no popup appears: Press F1 → Type: Dev Containers: Reopen in Container

5. VS Code will now build the Docker image → Create the container → Install all dependencies automatically

    ⚠️ Be patient. The first build may take several minutes.