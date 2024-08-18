ComfyUI-API
====

## Summary

This project gives a use case of [ComfyUI](https://github.com/comfyanonymous/ComfyUI) with [FLUX.1 Schnell](https://github.com/black-forest-labs/flux?tab=readme-ov-file#models) model that runs on [Modal](https://modal.com/).
It allows you to use FLUX.1 Schnell model on ComfyUI for purpose of image generation with any prompt you like on Modal's cloud service.
In addition, it allows you to invoke image generation from your local client through the web service to launch.

You need your account on Modal and capability run a small web application on Modal.

## How to run

### ComfyUI (GUI)

1. Launch ComfyUI API service.
```
git clone https://github.com/hajmf/comfyui-api.git
cd comfyui-api
modal serve app/comfy-api-app.py
```
2. After successful launch, open the URL showed in the terminal.

### ComfyUI (API) 

1. After successful launch, open the 2nd terminal.
2. Modify `prompt.txt`. Each prompt has to be in single line.
3. Modify `batch.py` to replace URL with your modal workspace name.
4. Run `batch.py`

## License

[MIT License](LICENSE)