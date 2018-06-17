#!/bin/sh
#celery multi start worker1 -A kct_wallet
celery -A MedicalDispenser worker -l info --autoscale=10,1 -B