Polish installation notes for HDFS:

1. Clone libhdfs3 from github:
    git clone git@github.com:Pivotal-Data-Attic/pivotalrd-libhdfs3.git libhdfs3

2. Install required packages
    sudo apt-get install cmake cmake-curses-gui libxml2-dev 
    libprotobuf-dev libkrb5-dev uuid-dev libgsasl7-dev protobuf-compiler
    protobuf-c-compiler build-essential -y

3. Use CMake to configure and build
   mkdir build
   cd build
   ../bootstrap
   make -j2
   make install

4. Add the following to your ~/.bashrc environment file:
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/<user>/<libhdfs3-path>/dist

5. source ~/.bashrc

