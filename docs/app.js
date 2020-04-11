class ImagePreview {
    constructor(canvasId) {
        this.canvasId = canvasId;
    }

    canvas() {
        return document.getElementById(this.canvasId);
    }

    clear() {
        this.canvas().getContext("2d").clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * @param Image
     */
    loadImage(image) {
        this.canvas().style.width ='100%';
        this.canvas().width  = this.canvas.offsetWidth;
        
        this.clear();

        image.onload = () => {
            var width = image.naturalWidth,
            height = image.naturalHeight;
            this.canvas().width = width;
            this.canvas().height = height * (this.canvas().width/width);
            this.canvas().getContext("2d").drawImage(image,0,0);
        }
    }

    drawBoundingBoxes(boundingBoxes) {
        var ctx = this.canvas().getContext("2d");
        
        var colours = [
            '#0075DC', '#990000', '#005C31', '#4C005C', '#808080',
            '#C20088', '#FFA405', '#9DCC00', '#F0A3FF', '#740AFF'
        ]

        for (var i=0; i < boundingBoxes.length; i++) {
            // bounding box
            ctx.strokeStyle = colours[boundingBoxes[i][0]]
            ctx.lineWidth = 5;
            ctx.strokeRect(boundingBoxes[i][2], boundingBoxes[i][3], boundingBoxes[i][4], boundingBoxes[i][5]);
            
            // label background
            ctx.fillStyle = colours[boundingBoxes[i][0]];
            ctx.fillRect(boundingBoxes[i][2], boundingBoxes[i][3]- 20, 20, 20);
            
            // label text
            ctx.font = "20px Arial";
            ctx.fillStyle = "#ffffff";
            ctx.fillText(boundingBoxes[i][0], boundingBoxes[i][2] + 5, boundingBoxes[i][3] - 2);
        }
    }
}
var app = new Vue({
    el: '#app',
    data: {
      loading: false,
      groundTruthReading: '',
      error: '',
      prediction: '',
      preview: new ImagePreview('preview')
    },
    methods: {
        showImage: function(event) {
            var input = event.target;
            this.prediction = '';
            this.groundTruthReading = '';
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = (e) => {
                    var image = new Image();
                    image.src = e.target.result;
                    this.preview.loadImage(image);
                }
                reader.readAsDataURL(input.files[0]);
            }
        },
        onSubmit: function(e) {
            e.preventDefault();
            e.stopPropagation();
            var file = document.getElementById("evidence").files[0]
            
            this.error = false;

            if (!file) {
                this.error = "Please upload an image of a meter";
                return;
            }
            
            if (!this.groundTruthReading) {
                this.error = "Please enter the displayed meter read";
                return;
            }
            
            var reader = new FileReader();
            this.loading = true;
            this.prediction = '';
            
            reader.onloadend = () => {
                data = {
                    "reading": this.groundTruthReading,
                    "evidence": btoa(reader.result)
                }
            
                fetch('https://aqjt2al8yj.execute-api.eu-west-1.amazonaws.com/staging/resource', {
                  method: 'POST', // or 'PUT'
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(data),
                })
                .then((response) => response.json())
                .then((data) => {
                    this.loading = false;
                    this.preview.drawBoundingBoxes(data['digits'])
                    this.prediction = data['predictedReading'];
                })
                .catch((error) => {
                    this.loading = false;
                    console.error('Error:', error);
                });
            }
            reader.readAsBinaryString(file)
        }
    }
});