#!/bin/bash
start_time=`date`
source ../build/envsetup.sh
echo "Building avatar..."
cd avatar && mm -B && cd ../
echo "Building grape..."
cd grape && mm -B && cd ../
echo "Building watermelon..."
cd watermelon && mm -j 4 -B && cd ../
echo "Building melon..."
cd melon && mm -B && cd ../
echo "Building lemon..."
cd lemon && mm -B && cd ../
#echo "Building service..."
#cd service && mm -j 4 -B && cd ../
echo "Building security..."
cd security && mm -B && cd ../

#echo "Building app..."
#cd app && mm -B && cd ../

echo "Building server..."
cd server && mm -B && cd ../

#echo "Building adapter..."
#cd adapter && mm -j 4 -B && cd ../
./get_so.sh
end_time=`date`
echo "$start_time -> $end_time"
