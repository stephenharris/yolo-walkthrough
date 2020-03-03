# Yolo


## Local set-up

On the local machine run

    xhost +local:docker

    docker-compose up --build

Then, to test, on the running container

    cd darknet
    ./darknet

You should get the output:

    usage: ./darknet <function>

To test the OpenCV/Display run

    ./darknet imtest data/eagle.jpg

(you should see eagles - but this will fail if you're running it on a headless EC2 instance.)

## Running some tests

Refs: 
 - https://pjreddie.com/darknet/yolo/
 - https://danielcorcoranssql.wordpress.com/2018/12/24/yolov3-custom-model-training-nfpa-dataset
 
Download some weights:

    mkdir weights
    wget -O weights/yolov3.weights https://pjreddie.com/media/files/yolov3.weights

Then, in `/home/jovyan/darknet`

    ./darknet detect cfg/yolov3.cfg ../weights/yolov3.weights data/dog.jpg

## Project walkthrough

Refs:
 - https://medium.com/@manivannan_data/how-to-train-yolov3-to-detect-custom-objects-ccbcafeb13d2 (updated version of below for yolov2)
 - https://medium.com/@manivannan_data/how-to-train-yolov2-to-detect-custom-objects-9010df784f36 (contains links to datasets)
 - https://danielcorcoranssql.wordpress.com/2018/12/24/yolov3-custom-model-training-nfpa-dataset


### Collecting your data

You can download an example data set from <https://www.dropbox.com/s/pfbjh7811mok7k5/NFPA_dataset.zip?dl=0> (it contains the annotations so you can skip the next step *Labelling data*).

Store the images in `data/images` and annotations in `data/labels`

### Labelling data 

For each image there needs to be `.txt` file, with the same filename, which labels the data (in particular, the width, height and co-ordinates of the centre of each bounding box (all given as ratios of the image's height/width), and the class number of the object contained by the box). Each line in this file corresponds to an object in the corresponding image.

    <class number box1> <box1 cx ratio> <box1 cy_ratio> <box1 width ratio> <box1 height ratio>
    <class number box2> <box2 cx ratio> <box2 cy ratio> <box2 width ratio> <box2 height ratio>

To achieve this I used https://github.com/tzutalin/labelImg


xhost +local:docker

docker run --rm -it -e DISPLAY=unix$DISPLAY --workdir=/home -v "${PWD}:/home" -v /tmp/.X11-unix:/tmp/.X11-unix tzutalin/py2qt4

python labelImg.py


At the end of this you should have two folders containing:

 - images of counters (e.g. 000001.jpg, 000002.jpg, ...)
 - annotations of the digits (e.g 000001.txt, 000002.txt, ...)


To view the results of the data you can run

    python digit-frequency.py /path/to/anotations/

### Creating the test and train data

    python split-train-test-data.py /path/to/images/


### Training (on AWS EC2)

Most of this applies when you're running it locally or on some other cloud service, but details may vary slightly).

#### Pre-requisite set up

See `terraform`. This creates:

 - EC2 instance (`p2.xlarge`, with CUDA installed)
 - 2 S3 buckets to store training data, initial weights and configs

Additionally for deploying our trained model

 - 1 S3 bucket to use a source for inference 
 - Lambda which runs our inference
 - API Gateway which provides an API interface for the lambda

(and all the necessary security groups / policies etc)

1. ssh into the instance and install depedencies 

    sudo yum install -y git opencv opencv-devel opencv-python gcc gcc-c++

2. Install Darknet. Checkout the darknet repo

    git clone https://github.com/pjreddie/darknet.git

Next edit `Makefile`. Set `GPU=1` and `CUDNN=1` if using GPU (and using CUDO). Set `OPENCV=1` and `OPENMP=1` (if you're running this on multiple cores). To create an `so` library, set `LIBSO=1`.

    cd darknet && make

To test

    ./darknet

You should get the output:

    usage: ./darknet <function>

To test the OpenCV/Display run

    ./darknet imtest data/eagle.jpg

(you should see eagles - but this will fail if you're running it on a headless EC2 instance.)

#### Configuration

1. Set up the config file. For this I've taken a copy of `yolov3-tiny.cfg` (see `cfg/counters-yolov3-tiny.cfg`)

Configure the batch and subdivision. I've used

    batch=32
    subdivisions=8

Set `classes` to the number of classes you'll be detecting on lines 135 and 177. In this example, 1.

Set `filters` on line 127 and 171 according to following formula

    filters=(10 + 5)*3

For example, with `classes =10`, `filters` is set to 45.

2. Upload the images, annotations train and test files (ensure the train and test files have the correct path to the images). (**Note:** Darknet, when looking for an image's annotation file, will take the image path, replace  "images" and "JPEGImages" with "labels", and the JPG extension with a .txt extension)

3. Uploade the names file (`cfg/counters.names`)

4. Create weights output directory

5. Update (and edit) the data file (`cfg/counters.data`)

    classes= 10
    train  = /path/to/train.txt  
    valid  = /path/to/test.txt  
    names = cfg/counters.names  
    backup = backup

`classes` is the number of classes you'll be detecting. `train`, `valid` and `names` are the paths to the files uploaded in (2) and (3). `backup` is the path to the directory we created in (4).

6. Generate anchors for your training data

    ./darknet detector calc_anchors ./cfg/counter.data -num_of_clusters 6 -width 416 -height 416

7. Transfer learning from the UFPR dataset

    ./darknet partial cfg/counter-yolov3-tiny.cfg pretrained/counter-yolov3-tiny_best.weights pretrained/counter-ufpr.conv.11

#### Running the training

    nohup /home/ec2-user/darknet/darknet detector train cfg/counters.data cfg/counters-yolov3-tiny.cfg darknet53.conv > /var/log/darknet.counters.log &

You can then check progress by 

    tail -10 /var/log/darknet.counters.log.
    
or 

    grep "avg" /var/log/darknet.counters.log


## Resources

- https://pjreddie.com/darknet/install/ (Installation guide for darknet)
- https://github.com/AlexeyAB/darknet
- https://medium.com/@manivannan_data/how-to-train-yolov3-to-detect-custom-objects-ccbcafeb13d2 (updated version of below for yolov2)
- https://medium.com/@manivannan_data/how-to-train-yolov2-to-detect-custom-objects-9010df784f36 (contains links to datasets)
- https://danielcorcoranssql.wordpress.com/2018/12/24/yolov3-custom-model-training-nfpa-dataset/ Walkthrough of a the same example using NPFA data

- http://arxiv.org/abs/1506.02640 (YOLO paper, explains some of the configuration parameters)
- https://blog.francium.tech/custom-object-training-and-detection-with-yolov3-darknet-and-opencv-41542f2ff44e (blog explaining the entire process, uses alternative labelling tool: https://github.com/tzutalin/labelImg)

- https://www.learnopencv.com/training-yolov3-deep-learning-based-custom-object-detector/ (explains the configurations, also has link to datatsets, plus code: https://github.com/spmallick/learnopencv)
- https://towardsdatascience.com/tutorial-build-an-object-detection-system-using-yolo-9a930513643a

- possible alternative strategy: use ocr on extracted counter

