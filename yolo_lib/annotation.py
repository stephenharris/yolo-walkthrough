class Annotation(object):

    def __init__(self, className, centreX, centreY, width, height):
        self.className = className
        self.centreX = centreX
        self.centreY = centreY
        self.width = width
        self.height = height
        
    def __str__(self):
        return "{0} {1} {2} {3} {4}".format(self.className, self.centreX, self.centreY, self.width, self.height)

    # Create based on class name:#
    # 0 0.09534534534534535 0.463855421686747 0.0945945945945946 0.6626506024096386
    def create_from_string(type):
        parts = type.split()
        return Annotation(str(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]))
    
    def create_from_file(filename):
        f = open(filename, "r")        

        contents = list(map(lambda x: x.strip(), f.read().splitlines()))
        annotations = list(map(lambda line: Annotation.create_from_string(line), contents))
        return annotations;
    
    create_from_string = staticmethod(create_from_string)
    create_from_file = staticmethod(create_from_file)