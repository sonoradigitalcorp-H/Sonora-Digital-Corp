#!/bin/bash
# SDC Nightly Client Health Report
cd /home/ubuntu/sonora-digital-corp || exit 1
python3 -m apps.tenants.monitor --report >> /home/ubuntu/sonora-digital-corp/state/nightly-report.log 2>&1
