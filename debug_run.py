import sys
sys.stdout = sys.stderr = open('debug_log.txt', 'w')
print("START OF DEBUG", file=sys.__stdout__)
import os
os.chdir('d:/dev/tdx')
print("Changed dir", file=sys.__stdout__)
sys.path.insert(0, 'd:/dev/tdx')
print("Added path", file=sys.__stdout__)
from xg import main
print("Imported", file=sys.__stdout__)
main()
print("Done", file=sys.__stdout__)
