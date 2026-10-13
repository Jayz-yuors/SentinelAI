import argparse, json
from .orchestrator import Phase7Orchestrator

def main():
    p=argparse.ArgumentParser(prog="sentinelai-phase7")
    sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("prepare"); r.add_argument("repository_path")
    r.add_argument("--push",action="store_true")
    args=p.parse_args()
    if args.command=="prepare":
        result=Phase7Orchestrator().start(args.repository_path,push=args.push)
        print(json.dumps(result.__dict__,indent=2))

if __name__=="__main__": main()
