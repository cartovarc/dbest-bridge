
# DBEST-BRIDGE

## Introduction

IOT solution that bridges a serial communication interface and an http server for DBEST battery exchanger system. This script was tested in python 3.6.9 and 2.7.15.

## Installation

Install flask, pyserial and fix

    pip install requirements.txt

Add yourself to the `dialout` group. You will have to logout and then log back in before the group change is recognized.

    sudo adduser YOURUSER dialout

Schedule  cron job after system reboot, with crontab add following line:

    @reboot python /YOUR/PATH/TO/REPO/DBEST-BRIDGE/DBEST.py
