import argparse
from pathlib import Path
import time
import requests

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def main(args: argparse.Namespace):
  url = args.modalurl
  if not url.endswith('/'):
    url = url + '/'

  print(f"URL: {url}")
  data = {
    "prompt": args.prompt,
  } 
  print(f"Client for FLUX.1 Schnell Workflow running at server-side.")
  print(f"Sending request to {url}")
  # print(f"Prompt: {data['prompt']}")
  print(f"Parameter: {data}")
  print("Waitng for response.")
  
  start_time = time.time()
  res = requests.post(url, json=data)
  if res.status_code == 200:
    end_time = time.time()
    print(f"Successfully finished in {end_time - start_time} s.")
    filename = OUTPUT_DIR / f"{slugify(args.prompt)}.png"
    filename.write_bytes(res.content) 
    print(f"Saved to '{filename} .")
  else:
    if res.status_code == 404:
      print(f"Workflow API not found at {url}")
    res.raise_for_status()
  
def parse_args(arglist: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  
  parser.add_argument(
    "--modalurl",
    type=str,
    required=True,
    help="URL for modal ComfyUI app with the defined FLUX.1 Schnell image generation workflow.",
  )
  parser.add_argument(
    "--prompt",
    type=str,
    required=True,
    help="What to draw the by generative AI model."
  )
  return parser.parse_args(arglist[1:])

def slugify(s: str) -> str:
  return s.lower().replace(" ","-").replace(".","-").replace("/","-").replace(",","-")[:32]

import sys

if __name__ == "__main__":
  args = parse_args(sys.argv)
  main(args)