import argparse
parser = argparse.ArgumentParser()
parser.add_argument("host", help="hostaddress of the pacs server",
                    type=int)
args = parser.parse_args()
print(args.host)
