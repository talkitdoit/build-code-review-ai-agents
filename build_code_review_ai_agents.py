from openai import OpenAI
import os
import time
from icecream import ic
import shutil
import tiktoken

# Configuration
MAX_RETRIES = 5  # Maximum number of retries when rate limit is hit
RETRY_DELAY = 2  # Initial delay in seconds for retrying requests

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Tokenizer Setup
encoder = tiktoken.encoding_for_model("gpt-4")

# Tool for reading the file (simulating FileReadTool)
def file_read_tool(file_path):
    # Check if file exists before reading
    if not os.path.exists(file_path):
        ic(f"File {file_path} does not exist. Attempting to create it.")
        # Copy from input if recommit file doesn't exist
        if file_path == "recommit/main.tf":
            if not os.path.exists("inputs/main.tf"):
                raise FileNotFoundError("The source file 'inputs/main.tf' does not exist.")
            if not os.path.exists("recommit"):
                os.makedirs("recommit")
            shutil.copy("inputs/main.tf", "recommit/main.tf")
            ic(f"Copied 'inputs/main.tf' to 'recommit/main.tf'")
        else:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    ic(f"Reading file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content

# Base Agent Class
class Agent:
    def __init__(self, role, goal, file_path):
        self.role = role
        self.goal = goal
        self.file_path = file_path
        ic(f"Initializing Agent with role: {self.role}, goal: {self.goal}, file: {self.file_path}")
        self.content = file_read_tool(file_path)

    def review(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def estimate_tokens(self, prompt):
        tokens = len(encoder.encode(prompt))
        ic(f"Estimated tokens for prompt: {tokens}")
        return tokens

    def log_token_forecast(self, tokens):
        log_path = "outputs/tokenforecasts.log"
        if not os.path.exists("outputs"):
            os.makedirs("outputs")
        with open(log_path, 'a') as log_file:
            log_file.write(f"Estimated tokens: {tokens}\n")
        ic(f"Logged token forecast to: {log_path}")

    def generate_comments(self, prompt):
        retry_count = 0
        estimated_tokens = self.estimate_tokens(prompt)
        self.log_token_forecast(estimated_tokens)
        ic(f"Estimated cost for {estimated_tokens} tokens")

        while retry_count < MAX_RETRIES:
            try:
                ic(f"Generating comments with prompt: {prompt[:100]}...")  # Print the first 100 characters of the prompt for debugging
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                ic(f"Received response: {response}")
                return response.choices[0].message.content.strip()

            except client.error.RateLimitError as e:
                retry_count += 1
                ic(f"Rate limit error occurred (attempt {retry_count}): {e}")
                time.sleep(RETRY_DELAY * retry_count)  # Exponential backoff

        # If all retries are exhausted
        return "Unable to generate comment due to rate limit."

# Specialized Agents

# Syntax Agent
class SyntaxAgent(Agent):
    def review(self):
        ic(f"Reviewing syntax for file: {self.file_path}")
        issues = []
        prompt = "Identify any syntax issues in the following Terraform code:\n\n" + "".join(self.content)
        comments = self.generate_comments(prompt)
        issues.append(comments)
        return issues

# Best Practices Agent
class BestPracticesAgent(Agent):
    def review(self):
        ic(f"Reviewing best practices for file: {self.file_path}")
        issues = []
        prompt = "Check the following Terraform code for best practice violations, such as hardcoded secrets or missing tags:\n\n" + "".join(self.content)
        comments = self.generate_comments(prompt)
        issues.append(comments)
        return issues

# Optimization Agent
class OptimizationAgent(Agent):
    def review(self):
        ic(f"Reviewing optimizations for file: {self.file_path}")
        issues = []
        prompt = "Review the following Terraform code for any optimization suggestions related to resource usage or cost reduction:\n\n" + "".join(self.content)
        comments = self.generate_comments(prompt)
        issues.append(comments)
        return issues

# Writing Comments to New File
class ReviewAgentWithComments(Agent):
    def comment(self, issues):
        ic(f"Adding comments to file: {self.file_path}")
        report_path = "outputs/review_report.txt"
        output_path = "recommit/main.tf"
        report_content = []

        # Write comments to report file
        with open(report_path, 'w') as report_file:
            for issue in issues:
                report_content.append(issue)
                report_file.write(issue + '\n')
        ic(f"Writing review report to: {report_path}")

        # Add inline comments to the HCL file
        ic("Starting to add inline comments to the HCL file.")
        added_lines = set()

        # Iterate in reverse to avoid affecting line numbers while inserting comments
        for i in range(len(self.content) - 1, -1, -1):
            line = self.content[i]
            ic(f"Processing line {i + 1}: {line.strip()}")
            if (line.strip().startswith("resource") or line.strip().startswith("module") or line.strip().startswith("data")) and i not in added_lines:
                # Extract only the block starting at the current line
                block_lines = [line]
                j = i + 1
                while j < len(self.content) and self.content[j].strip() and not self.content[j].strip().startswith(('resource', 'module', 'data')):
                    block_lines.append(self.content[j])
                    j += 1
                block_content = "".join(block_lines)

                # Generate a concise comment for the current block only
                block_prompt = f"Provide a very short, one-sentence description of the following Terraform block only:\n\n{block_content}"
                comment = self.generate_comments(block_prompt)

                # Insert the generated comment above the current block
                comment_line = f"# {comment}\n"
                self.content.insert(i, comment_line)
                added_lines.add(i)
                ic(f"Added comment to line {i + 1}: {comment.strip()}")

        # Writing the reviewed content to output file
        ic(f"Writing reviewed content to: {output_path}")
        with open(output_path, 'w') as file:
            file.writelines(self.content)
        ic("Finished writing reviewed content to the output file.")

# Testing the Agents
if __name__ == "__main__":
    ic("Starting testing of agents")

    # Initialize agents using the original input file
    syntax_agent = SyntaxAgent("code analyzer", "Identify syntax issues", "inputs/main.tf")
    best_practices_agent = BestPracticesAgent("best practices checker", "Identify best practices violations", "inputs/main.tf")
    optimization_agent = OptimizationAgent("optimization checker", "Suggest optimizations", "inputs/main.tf")

    agents = [syntax_agent, best_practices_agent, optimization_agent]
    all_issues = []
    for agent in agents:
        ic(f"Running review for agent: {agent.role}")
        issues = agent.review()
        all_issues.extend(issues)
        ic(f"Issues found by {agent.role}: {issues}")

    # Adding comments to the file in the recommit directory
    review_agent_with_comments = ReviewAgentWithComments("commenter", "Add comments to file", "recommit/main.tf")
    review_agent_with_comments.comment(all_issues)
    ic("Completed testing of agents")
