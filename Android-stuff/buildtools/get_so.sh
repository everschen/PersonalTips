#!/bin/bash

path1=~/sprd7.0_dev/out/target/product/sp9832a_2h11/system/
path2=~/sprd7.0_dev/out/target/product/sp9832a_2h11/symbols/system/
target1=~/sprd7.0_dev/output/
target2=~/sprd7.0_dev/output/symbols/

cp -p $path1/lib/libavatar.so $target1
cp -p $path1/lib/libzmf.so $target1
cp -p $path1/lib/libCamdrv24.so $target1
cp -p $path1/lib/libmme_jrtc.so $target1
cp -p $path1/lib/liblemon.so $target1
cp -p $path1/lib/liblemon.so $target1
cp -p $path1/../obj/JAVA_LIBRARIES/vowifi_sdk_intermediates/javalib.jar $target1/vowifi_sdk.jar

cp -p $path2/lib/libavatar.so $target2
cp -p $path2/lib/libzmf.so $target2
cp -p $path2/lib/libCamdrv24.so $target2
cp -p $path2/lib/libmme_jrtc.so $target2
cp -p $path2/lib/liblemon.so $target2

#cp -p $path1/priv-app/justex/justex.apk $target1
#cp -p $path1/priv-app/service/service.apk $target1
cp -p $path1/priv-app/Security/Security.apk $target1
cp -p $path1/bin/ju_ipsec_server $target1/ju_ipsec_server
#cp -p $path1/framework/vowifi_adapter_dex.jar $target1/vowifi_adapter.jar

#cp -p ~/output/* ~/20160628/sprdroid6.0_trunk_vowifi_dev3/output/
#cp -p ~/output/symbols/* ~/20160628/sprdroid6.0_trunk_vowifi_dev3/output/symbols/

echo "ls -lt $target1"
ls -lt $target1
