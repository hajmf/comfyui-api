import modal
import subprocess

image = (
  modal.Image.debian_slim (python_version="3.11")
  .apt_install("git")
  ### Install comfy
  .pip_install("comfy-cli==1.0.36")
  .run_commands("comfy --skip-prompt install --nvidia")
  ### Install FLUX.1 model and encoders.
  .run_commands( # FLUX.1 Schnell model
    "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors --relative-path models/unet"
  )
  .run_commands( # FLUX.1 T5xx text encoder (fp8)
    "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors --relative-path models/clip"
  )
  .run_commands( # FLUX.1 T5xx text encoder (fp16)
    "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors --relative-path models/clip"
  )
  .run_commands( # FLUX.1 CLIP-L text encoder
    "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip"
  )
  .run_commands( # FLUX.1 VAE
    "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors --relative-path models/vae"
  )
  .copy_local_file( ## comfy_cli/command/run.py::execute() must be modified with timeout of ~300s.
    local_path="../modal_comfy/lib/python3.10/site-packages/comfy_cli/command/run.py",
    remote_path=" /usr/local/lib/python3.11/site-packages/comfy_cli/command",
  )
)
# app = modal.App(name="example-comfyui", image=i1200mage)
app = modal.App(name="comfy-api", image=image)

@app.function(
  gpu="T4",
  concurrency_limit=1,
  allow_concurrent_inputs=10,
  container_idle_timeout=600,
  timeout=3600,
)
@modal.web_server(8000, startup_timeout=60)
def ui():
  subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)

workflow_filename = "flux1_schnell_workflow_api.json"
### Background container for API
import json
import uuid
from pathlib import Path
from typing import Dict
@app.cls(
  concurrency_limit=1,
  allow_concurrent_inputs=10,
  container_idle_timeout=600,
  gpu="T4",
  mounts=[
    modal.Mount.from_local_file(
      Path(__file__).parent / workflow_filename,
      "/root/" + workflow_filename
    ),
  ],
)
class ComfyUI:
  @modal.enter()
  def launch_comfy_background(self):
    print(f"Comfy process is going to run in background.")
    cmd = "comfy launch --background"
    # cmd = "comfy launch --background -- --timeout 300" <- cannot change timeout
    subprocess.run(cmd, shell=True, check=True)
    print(f"Comfy process is running.")
  
  @modal.method()
  def infer(self, workflow_path: str):
    print(f"Workflow is going to run.")
    cmd = f"comfy run --workflow {workflow_path} --wait"
    subprocess.run(cmd, shell=True, check=True) #need timeout = 1200?
    print(f"Workflow is done.")
    
    output_dir = "/root/comfy/ComfyUI/output"
    workflow = json.loads(Path(workflow_path).read_text())
    file_prefix = [
        node.get("inputs")
        for node in workflow.values()
        if node.get("class_type") == "SaveImage"
    ][0]["filename_prefix"]
    print(f"Output is saved in {output_dir} .")

    for f in Path(output_dir).iterdir():
      if f.name.startswith(file_prefix):
        return f.read_bytes()
  
  @modal.web_endpoint(method="POST")
  def api(self, item: Dict):
    from fastapi import Response
    print("API hooked.")
    workflow_data = json.loads(
      (Path("/root") / workflow_filename).read_text()
    )
    print(f"Prompt received: {item['prompt']}")
    workflow_data["6"]["inputs"]["text"] = item["prompt"]
    client_id = uuid.uuid4().hex
    workflow_data["9"]["inputs"]["filename_prefix"] = client_id
    new_workflow_file = f"{client_id}.json"
    print(f"Workflow to run is saved: {new_workflow_file}")
    json.dump(workflow_data, Path(new_workflow_file).open("w"))
    
    img_bytes=self.infer.local(new_workflow_file)
    
    return Response(img_bytes, media_type="image/jpeg")
