set -e

echo "Start training at $(date +"%D %T")"
nohup /home/ubuntu/darknet/darknet detector train ${DATA_CFG} ${MODEL_CFG} ${PRETRAINED_WEIGHTS} -dont_show -mjpeg_port 8090 -map > /home/ubuntu/yolo.log &

# to continue, for example:
#nohup /home/ubuntu/darknet/darknet detector train ${DATA_CFG} ${MODEL_CFG} /home/ubuntu/backup/counters-yolov3-tiny_12000.weights -dont_show -mjpeg_port 8090 -map > /home/ubuntu/yolo.log &

echo "Finished training at $(date +"%D %T")"
