# Stable Diffusion API Server

## Requirements

1. Install Python.
1. Install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/download.html).
1. Download this repo.
1. cd into the repo's directory.
1. Set up a [conda](https://conda.io) environment named `sd-api-server` using the following commands:

```
% conda env create -f environment.yaml
% conda activate sd-api-server
```

You'll also need [a HuggingFace token](https://huggingface.co/settings/tokens). Paste your token into the `token.txt` file, and be sure to save it.

## To Run

```
% python3 server.py
```