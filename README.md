
# build code review ai agents youtube series!

This repository contains code for building custom AI AGENTS to automate code reviews on Infrastructure-as-Code (IaC) files, and starting with Terraform code. The AI agents are built using custom classes in Python and use the OpenAI API to generate comments on syntax, best practices, and optimization suggestions. This project serves as the codebase for the video tutorial series, “How to Build AI Agents to Review Your Code Using Custom Python Classes Only!”

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Example Terraform Code](#example-terraform-code)
- [Next Steps](#next-steps)

## Overview
The code in this repository defines a system of specialized agents that analyze and comment on Terraform code. Each agent serves a unique purpose:
- **SyntaxAgent**: Checks for syntax issues.
- **BestPracticesAgent**: Identifies best practice violations.
- **OptimizationAgent**: Suggests optimization opportunities.

The `ReviewAgentWithComments` class combines the outputs of all agents and adds comments directly to the Terraform code.

## Features
- Automated syntax checks, best practice validation, and optimization suggestions.
- Uses the OpenAI API to generate human-readable comments.
- Adds inline comments to Terraform code for easy review.

## Prerequisites
- Python 3.7 or later
- An OpenAI API key (set as an environment variable)

## Tools Used

This project was developed and tested using the following tools:

- **Python**: v3.13
- **pip**: v24.2
- **Nushell**: A modern shell environment for productivity
- **Zed IDE**: A lightweight and efficient code editor for streamlined development
- **Git**: 2.47.0

Make sure to have similar versions or compatible setups for the best results when following along.

## Setup Instructions

### Step 1: Clone the Repository
First, clone this repository to your local machine:
```bash
git clone https://github.com/talkitdoit/build-code-review-ai-agents.git
cd build-code-review-ai-agents
```

### Step 2: Create Required Directories and Files
Make sure the required directories and input files are set up:
```bash
# Create necessary directories
mkdir -p inputs recommit outputs && touch inputs/main.tf

# Place your Terraform code in `inputs/main.tf`
# An example Terraform file is provided in this repository.
```

### Step 3: Install Python and pip (if not already installed)
Ensure you have Python and pip installed. You can verify with:
```bash
python3 --version
pip3 --version
```

If not installed, follow [Python’s official installation guide](https://www.python.org/downloads/).

### Step 4: Set the OpenAI API Key
Export your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Step 5: Set Up Python Virtual Environment
Create a virtual environment to manage dependencies:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Step 6: Install Required Python Packages
Install the necessary packages using pip:
```bash
pip install -r requirements.txt
```

> Note: The `requirements.txt` file should include dependencies like `openai`, `icecream`, and `tiktoken`.

## Usage

### Running the Code
To test the AI code review agents on your Terraform code, run the following command in the terminal:

```bash
python main.py
```

This will:
1. Initialize instances of each agent.
2. Run a review on the Terraform code located in `inputs/main.tf`.
3. Generate a `review_report.txt` in the `outputs` directory and add inline comments to `recommit/main.tf`.

### Expected Output
- **recommit/main.tf**: Contains the original Terraform code with AI-generated inline comments.
- **outputs/review_report.txt**: A report file with details on the issues identified by each agent.

## Example Terraform Code
Place your Terraform code in `inputs/main.tf`. Here’s an example of what it might look like (or use the one provided):

<details>
  <summary>Click to expand Terraform code example</summary>

```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  tags = {
    Name = "example-instance"
  }
}

module "storage_account" {
  source                      = "./modules/storage_account"
  name                        = "${local.storage_account_prefix}${random_string.storage_account_suffix.result}"
  location                    = var.location
  resource_group_name         = azurerm_resource_group.rg.name
  account_kind                = var.storage_account_kind
  account_tier                = var.storage_account_tier
  replication_type            = var.storage_account_replication_type
  tags                        = var.tags

}

data "azurerm_client_config" "current" {
}
```
</details>

The agents will analyze this file and add comments for syntax, best practices, and optimization opportunities.

## Next Steps
In future parts of this tutorial series, we will:
1. Integrate these AI agents into a GitHub Actions pipeline.
2. Extend the functionality to automatically add comments to pull requests.

Stay tuned for updates!

## License
This project is licensed under the MIT License.

## Contact
For questions or feedback, please reach out via GitHub issues
* [youtube](youtube.com/@talkitdoit)
* [x](x.com/talkitdoit)
* [tiktok](tiktok.com/@talkitdoit3)

---

Enjoy building your AI-driven code review agents!
