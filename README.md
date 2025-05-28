---
title: Template Final Assignment
emoji: 🕵🏻‍♂️
colorFrom: indigo
colorTo: indigo
sdk: gradio
sdk_version: 5.25.2
app_file: app.py
pinned: false
hf_oauth: true
# optional, default duration is 8 hours/480 minutes. Max duration is 30 days/43200 minutes.
hf_oauth_expiration_minutes: 480
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

## Local Setup

```sh
# Install dependencies
uv pip sync requirements.lock

# Update lock
uv pip compile requirements.txt -o requirements.lock
```

## Acknowledgements

Heavily inspired by https://huggingface.co/spaces/bstraehle/gaia
