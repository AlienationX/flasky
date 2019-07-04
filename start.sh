#!/usr/bin/env bash

gunicorn -b :5000 --access-logfile - --error-logfile - manage:app