import subprocess

filepath = "./prompt.txt"
# NOTE # Each prompt has to be in a single line without a new line.

modal_url='"https://yourusername--comfy-api-comfyui-api-dev.modal.run"'
# NOTE #  Please replace yourusername with your username

with open(filepath, 'r') as f:
  for prompt in f:
    cmd = f"python app/comfy-api-client.py --modalurl {modal_url} --prompt \"{prompt}\""
    print(f"exec: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
