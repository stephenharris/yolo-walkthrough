FROM "jupyter/scipy-notebook"

RUN wget -O darknet.zip https://github.com/AlexeyAB/darknet/archive/master.zip && unzip darknet.zip
RUN mv darknet-master darknet

USER root
RUN apt-get -y update && apt-get -y install libopencv-dev

USER jovyan

RUN pip install unittest-data-provider

RUN sed -i 's/OPENCV=0/OPENCV=1/g' darknet-master/Makefile
RUN cd darknet-master && make
