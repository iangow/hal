'''
    python text.py 820774/000093639206000657

Print out the cleaned text associated with this filing. This is useful
for creating target files.
'''

from models import Filing
import sys

if __name__ == '__main__':
    script, folder = sys.argv
    filing = Filing.get(folder)
    print filing.text()
