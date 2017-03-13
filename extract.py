import random
import sys

def write_data(filename, data):
    f = open(filename, 'w')
    for line in data:
        f.write(line)
        
def split_data(filename):
    f = open(filename, 'r')

    training = []
    held_out = []
    test = []
    
    for line in f:
        rand_num = random.uniform(0,1)
        if rand_num < 0.7:
            training.append(line)
        elif rand_num < 0.85:
            held_out.append(line)
        else:
            test.append(line)

    write_data("training.txt", training)
    write_data("heldout.txt", held_out)
    write_data("test.txt", test)

split_data("spambase.data")