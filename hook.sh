#!/bin/bash

args=$@

/usr/local/bin/inwx-hook.py $args

systemctl reload apache2
