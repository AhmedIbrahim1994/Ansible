import argparse
parser = argparse.ArgumentParser()
#parser.add_argument("echo", help="insert echo", type=string)
args = parser.parse_args()
print args.echo

