import subprocess
import os

def generate_fake_graph(graph_dir, to_clean = False):
    '''
    generates a fake point distribution. if to_clean is true, will always generate
    a new one
    returns the filenames of the csv containing lat/long info of the points and the
    labels of the points
    '''
    to_run = ['python', 'src/preprocessing/generate-fake-graph.py', '-d', graph_dir]
    pointsfile = os.path.join(graph_dir, 'points.csv')
    labelfile = os.path.join(graph_dir, 'labels.csv')
    if not to_clean and os.path.isfile(pointsfile) and os.path.isfile(labelfile):
        return pointsfile, labelfile
    subprocess.call(to_run)
    if os.path.isfile(pointsfile) and os.path.isfile(labelfile):
        return pointsfile, labelfile
    else:
        raise FileNotFoundError
    
