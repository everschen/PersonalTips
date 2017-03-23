#!/bin/bash

source ../build/envsetup.sh

echo "Building avatar..."
cd avatar && mm -j 4 && cd ../
echo "Building grape..."
cd grape && mm -j 4 && cd ../
echo "Building watermelon..."
cd watermelon && mm -j 4 && cd ../
echo "Building melon..."
cd melon && mm -j 4 && cd ../
echo "Building lemon..."
cd lemon && mm -j 4 && cd ../
echo "Building security..."
cd security && mm -j 4 && cd ../

echo "Building server..."
cd server && mm -j 4 && cd ../
./get_so.sh
