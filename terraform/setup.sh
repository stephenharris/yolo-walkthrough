sudo apt-get update
sudo apt-get install -y git 

git clone https://github.com/AlexeyAB/darknet.git

cat >> ~/.bash_profile << 'EndOfMessage'
export S3_BUCKET_NAME=compute-data-counter-wlw7bxjo
export PRETRAINED_WEIGHTS_FILENAME=yolov3-tiny.conv.11
export MODEL_CFG=./cfg/counter-yolov3-tiny.cfg
export DATA_CFG=./cfg/counter.data
export PRETRAINED_WEIGHTS=/home/ubuntu/${S3_BUCKET_NAME}/pretrained/${PRETRAINED_WEIGHTS_FILENAME}
EndOfMessage
source ~/.bash_profile

mkdir ${S3_BUCKET_NAME}

echo "Getting data from S3"
aws s3 sync s3://${S3_BUCKET_NAME}/training ${S3_BUCKET_NAME}/training/
aws s3 sync s3://${S3_BUCKET_NAME}/testing ${S3_BUCKET_NAME}/testing/
aws s3 sync s3://${S3_BUCKET_NAME}/pretrained ${S3_BUCKET_NAME}/pretrained/
aws s3 sync s3://${S3_BUCKET_NAME}/cfg ${S3_BUCKET_NAME}/cfg/

mkdir ${S3_BUCKET_NAME}/backup

find ${PWD}/${S3_BUCKET_NAME}/training/ -name "*.jpg" > ${PWD}/${S3_BUCKET_NAME}/train.txt
find ${PWD}/${S3_BUCKET_NAME}/testing/ -name "*.jpg" > ${PWD}/${S3_BUCKET_NAME}/test.txt

touch ${PWD}/${S3_BUCKET_NAME}/yolo.log && chmod u+rw ${PWD}/${S3_BUCKET_NAME}/yolo.log

cd ~/darknet;

sed -i 's/GPU=0/GPU=1/g' Makefile
sed -i 's/CUDNN=0/CUDNN=1/g' Makefile
sed -i 's/OPENCV=0/OPENCV=1/g' Makefile
sed -i 's/OPENMP=0/OPENMP=1/g' Makefile

make