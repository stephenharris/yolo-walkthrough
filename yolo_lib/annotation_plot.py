from .annotation import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def annotation_plot(image, annotations):

    fig,ax = plt.subplots(1)
    ax.imshow(image)

    # Display new bounding box
    for annotation in annotations:
        width = annotation.width * image.width
        height = annotation.height * image.height
        left = annotation.centreX* image.width - width/2
        top = annotation.centreY * image.height  - height/2

        rectYolo = patches.Rectangle((left,top),width,height,linewidth=1,edgecolor='b',facecolor='none')
        ax.add_patch(rectYolo)

    plt.show()