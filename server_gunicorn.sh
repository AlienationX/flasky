#!/usr/bin/env bash

gunicorn -w 4 -b :5000 --access-logfile - --error-logfile - manage:app