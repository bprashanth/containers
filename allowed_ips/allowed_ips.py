#! /bin/python3

import argparse
import datetime
import json
import subprocess
import sys


parser = argparse.ArgumentParser(description="allowed ips debugger",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-c", "--context", help="context for cluster")
args = parser.parse_args()


def shell(cmd):
    return subprocess.run(["sh", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode('utf-8')


def kubectl(cmd):
    kcmd = "kubectl %s" % cmd
    if args.context:
      kcmd = "kubectl --context %s %s" % (args.context, cmd)
    return shell(kcmd)


def check_allowed_ips():
    peer_debug_info = {}
    allowed_ips = []
    for anetd in kubectl("get po -n kube-system -l k8s-app=cilium -o jsonpath='{.items[*].metadata.name}'").split():
        print ("Scraping allowed ips from %s" % anetd)
        di = kubectl("exec %s -n kube-system -c cilium-agent -- cilium debuginfo --output json" % anetd)
        peer_debug_info[anetd] = json.loads(di)["encryption"]["wireguard"]["interfaces"][0]["peers"]
        for peers in peer_debug_info[anetd]:
            for ip in peers['allowed-ips']:
                # remote node ips are added as /24 cidrs so we discard them
                # we also don't bother with ipv6
                if ip.endswith("/32"):
                    allowed_ips.append(ip.rstrip("32").rstrip("/"))
    node_ips = []
    for n in kubectl("get no -o wide | awk -F' ' '{ print $6 }' | tail -n +2").split():
        node_ips.append(n)

    fail_ip = ""
    pod_ips = []
    script = "{range .items[*]}{@.status.phase}{\",\"}{@.status.podIP}{\" \"}{end}"
    for ip_phase in kubectl("get po -A -o jsonpath=\'%s\'" % script).split():
        if ip_phase.split(",")[0] != "Running":
            print ("ignoring pod in phase %s" % ip_phase)
            continue
        ip = ip_phase.split(",")[1]
        pod_ips.append(ip)
        if ip not in allowed_ips and ip not in node_ips:
            fail_ip = ip

    print("Allow ips: %s\npod ips  : %s\nnode ips : %s\n" % (allowed_ips, pod_ips, node_ips))
    if fail_ip == "":
        print("All Running pod ips in cilium allowed_ips.")
        return

    print(json.dumps(peer_debug_info, indent=2))
    print("Printing cilim endpoints")
    for ce in kubectl("get ciliumendpoints -A").split("\n"):
        print(ce)
    print("Printing pods")
    for po in kubectl("get po -A -o wide").split("\n"):
        print(po)
    for anetd in kubectl("get po -n kube-system -l k8s-app=cilium -o jsonpath='{.items[*].metadata.name}'").split():
        print ("Running cilium-bugtool for %s" % anetd)
        bt = kubectl("exec %s -n kube-system -c cilium-agent -- cilium-bugtool -o gz" % anetd)
        print(bt)
    sys.exit("IP %s not in allowed ips." % fail_ip)


def main():
    while True:
        print("Checking allowed_ips for consistency@%s" % datetime.datetime.now())
        check_allowed_ips()


if __name__ == "__main__":
    main()
