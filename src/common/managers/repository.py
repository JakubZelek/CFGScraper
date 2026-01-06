import json
import subprocess
from pathlib import Path


class RepositoryManager:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url

    def clone_and_build(self, repo_script: str):
        subprocess.run([repo_script, self.repo_url], check=True)

    def get_commit_hash(self, repo_path: str) -> str:
        
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def get_files(self, extension: str, folder: str):
        folder = Path(folder)
        ext = extension.lstrip(".")  # Handle both ".py" and "py"
        for filename in folder.rglob(f"*.{ext}"):
            yield filename

    def generate_cfg_from_file(self, filename: str, cfg_build_script: str):
        control_flow_graphs = subprocess.run(
            [cfg_build_script, filename], capture_output=True, text=True, check=True
        )
        return json.loads(control_flow_graphs.stdout)

    def rm(self, repo_dir):
        subprocess.run(["rm", "-rf", repo_dir], check=True)
