---
title: FOI Process Explorer
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
suggested_hardware: cpu-basic
pinned: false
license: apache-2.0
---

# FOI Process Explorer

Docker-served analytical dashboard for the reviewed, synthetic `foi-process` event-log dataset.

The checked-in demonstration data is generated from the dataset bundle and verified against its
SHA-256 manifest. The interface is read-only and does not make certified legal conclusions.

The Space uses the free CPU Basic hardware tier. It has no GPU or persistent-runtime requirement;
ZeroGPU is therefore intentionally not used.
