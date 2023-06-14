#! /bin/python3

import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser(description="node pod deleter",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--node", default="", help="node name on which pods must be deleted")
parser.add_argument("-c", "--context", default="", help="context for cluster")
args = parser.parse_args()


def shell(cmd):
    return subprocess.run(["sh", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode('utf-8')


def kubectl(cmd):
    kcmd = "kubectl %s" % cmd
    if args.context:
      kcmd = "kubectl --context %s %s" % (args.context, cmd)
    return shell(kcmd)


def delete_pods(n):
    script = "{range .items[*]}{@.spec.nodeName}{\",\"}{@.metadata.name}{\",\"}{@.metadata.namespace}{\" \"}{end}"
    for pod_info in kubectl("get po -A -o jsonpath=\'%s\'" % script).split():
        pod_info = pod_info.split(",")
        node = pod_info[0]
        pod_name = pod_info[1]
        pod_ns = pod_info[2]
        if node == n:
            print("Deleting pod %s" % pod_info)
            kubectl("delete po %s -n %s --force" % (pod_name, pod_ns))

if args.node == "":
    sys.exit("Need node name via --node")
print("Deleting pods on node %s" % args.node)
delete_pods(args.node)
