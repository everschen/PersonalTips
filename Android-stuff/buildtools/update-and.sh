#!/bin/bash

cd /home8/evers.chen/sprd7.0_dev/
cd vendor/sprd/proprietories-source/ims
repo sync .


cd /home8/evers.chen/sprd7.0_dev/
cd vendor/sprd/proprietories-source/ImsCM
repo sync .


cd /home8/evers.chen/sprd7.0_dev/
cd vendor/sprd/proprietories-source/ims_bridged
repo sync .


cd /home8/evers.chen/sprd7.0_dev/
cd vendor/sprd/proprietories-source/ril
repo sync .

cd /home8/evers.chen/sprd7.0_dev/
cd vendor/sprd/sprd_vowifi
repo sync .


cd /home8/evers.chen/sprd7.0_dev/
cd frameworks/opt/telephony
repo sync .

cd /home8/evers.chen/sprd7.0_dev/
cd frameworks/base/telephony
repo sync .

cd /home8/evers.chen/sprd7.0_dev/
cd kernel/net/ims_bridge
repo sync .

cd /home8/evers.chen/sprd7.0_dev/
cd kernel/include/linux/ims_bridge
repo sync .





