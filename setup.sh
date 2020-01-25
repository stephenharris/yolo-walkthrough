sudo apt-get update
sudo apt-get install -y git 

git clone https://github.com/AlexeyAB/darknet.git

cat >> ~/.bash_profile << 'EndOfMessage'
export S3_BUCKET_NAME=compute-data-f4sy2kau
export PRETRAINED_WEIGHTS_FILENAME=darknet53.conv.74
export MODEL_CFG=/home/ubuntu/cfg/counters-yolov3-tiny.cfg
export DATA_CFG=/home/ubuntu/cfg/counters.data
export PRETRAINED_WEIGHTS=/home/ubuntu/pretrained/${PRETRAINED_WEIGHTS_FILENAME}
EndOfMessage
source ~/.bash_profile

echo "Getting data from S3"
aws s3 sync s3://${S3_BUCKET_NAME}/training training/
aws s3 sync s3://${S3_BUCKET_NAME}/testing testing/
aws s3 sync s3://${S3_BUCKET_NAME}/pretrained pretrained/
aws s3 sync s3://${S3_BUCKET_NAME}/cfg cfg/

mkdir backup

find /home/ubuntu/training/ -name "*.jpg" > train.txt
find /home/ubuntu/testing/ -name "*.jpg" > test.txt

touch /home/ubuntu/yolo.log && chmod u+rw /home/ubuntu/yolo.log

cd darknet;

sed -i 's/GPU=0/GPU=1/g' Makefile
sed -i 's/CUDNN=0/CUDNN=1/g' Makefile
sed -i 's/OPENCV=0/OPENCV=1/g' Makefile
sed -i 's/OPENMP=0/OPENMP=1/g' Makefile

make