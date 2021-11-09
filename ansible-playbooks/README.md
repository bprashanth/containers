# Provisioning Clusters

## Quickstart

Currently cluster bootstrapping is only supported on linux laptops/servers.

### Remote cluster

First ensure you can ssh into the target IP
```
$ ssh -i ~/.ssh/<your_private_key_in_hosts_file> $USER@<ip_from_hosts_file>
```
If this works, then declare all the variables in the hosts.yaml file and run
```
$ ansible-playbook cluster_create.yaml -i hosts.yaml -v
```
If you only want to run a single task/sub-task (i.e you already have a
Kubeflow cluster which you want to reconfigure):
```
$ ansible-playbook cluster_create.yaml -i hosts.yaml --tags "config" -v
```
If you would like to inspect what exactly the "config" tag does, see this
[file](roles/kubeflow/tasks/config.yaml).

### Localhost

Setup a localhost cluster using `hack/local-up-cluster.sh`, then run
```
$ ansible-playbook cluster_create.yaml --connection local --inventory local, --tags "config" -v -K
```
Note a few caveats:

* This seems to only need the `-K` option (sudo password) because of a [ansible
  bug](https://github.com/ansible/ansible/issues/60833).
* `local-up-cluster.sh` will bring up an un-athenticated server.

## Provisioning Cycle

All hosts are created equal and then partitioned into master, worker/minion
roles. The `cluster_create.yaml` playbook creates a Kubernetes cluster and
invokes `post_create.yaml` at the end. The `post_create.yaml` playbook runs
roles that can only be run after the whole cluster is put toghether.

```
                All Hosts
                ---------
    [ common packages: docker, curl etc]
    [ kubernetes binaries: kubelet etc ]
                    |
    --------------------------------------
    |                                    |
    Master                              Minon
    ------                              -----
 [ apiserver, etcd ]        [ kubelet joins cluster ]
 [ kfctl create]            [ kubeflow pods ]
```

NB: in its current state, this repo only provisions master nodes. That too, it
does so using `kind` to allow for easy cleanup. So the Minion branch of the tree
above is a lie. Everything runs on master, including the Kubeflow pods.

## Kind

We deploy a single master/node via `kind`, a project to run Kubernetes within
docker. This is extremely convient in several ways.
1. Since we only have 1 on-prem box, it helps to not have to specify iptables
   rules directly on the host.
2. Moreover, any storage/networking configurations that leak out of the docker
   must be explicitly declared in the kind config and are easier to audit.
3. Bursting to the cloud is a lot easier. Setting up a hybrid cluster across
   prem-cloud is trikcy because IPs don't translate. It is a lot easier to spin
up larger preemptible VMs as single node kind clusters, train and spin them
down.

Overall, using kind at this stage just makes the cluster easier to manage,
especially since Kubernetes is *already running* on some of the existing DGX
boxes. However, this limits us in the following ways:
1. Adding a node to kind is [basically
unsupported](https://github.com/kubernetes-sigs/kind/issues/452)
    - This means we need to run 3 clusters, 1 per on-prem box/environement
2. We are dependent on kind to upgrade Kubernetes versions. When kind supports a
new version, we will have to delete the cluster, upgrade kind, create the
cluster.

### Transitioning off Kind

If we decide to transition off-of kind to running containers on bare-metal, we
will have to use a tool like
[kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
(which kind already uses under the hood). However if we migrate to the cloud we
can simply use a service like EKS to manage the cluster. Eitherways, the
operations to migrate data off-of a running Kubernetes cluster are the same:
backup etcd/nfs, restore etcd/nfs, delete all pods and wait for them to get
recreated. As long as all data is in NFS and all models are in wandb, we should
be OK.

To transition off of kind we need to decide where we're going *to*. Options
include: deploy Kubernetes via kubeadm, use an existing Kubernetes on-prem
managed cluster, move to EKS, move to something like Arrikto enterprise etc.
Currently we have 3 DGX boxes mapping to our 3 environments and lots of unkowns
to resolve before we can get more boxes/go to the cloud, so continuing to use
kind seems OK. This will, however, lead to a utilization hit of about 20% across
all 3 boxes and we need to weigh that against the effort to resolve some of the
unknowns blocking a better long term solution.

Hence it would be prudent to consider migrating to kubeadm before deploying kind
in the prod environment. In staging, all data should be stored in wandb/nfs and
users should be OK with best effort migration of the other yaml/pipeline
metadata.

## Storage

The main piece of storage in this cluster is the etcd data directory. Another
important piece to consider is the nfs root directory, when running against a
local NFS. As long as these 2 are backed up, the cluster and all its objects can
be restored quite easily in a different environment/vm/cloud.

### Etcd

The kind cluster uses a `hostPath` volume for etcd data
```
$ kubectl get po etcd-mls-control-plane -n kube-system -o yaml | grep -i etcd-data$ -B 3
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/lib/etcd
      name: etcd-data
--
  - hostPath:
      path: /var/lib/etcd
      type: DirectoryOrCreate
    name: etcd-data
```
Note that this is a hostPath *inside* the docker container, which translates to
a path like `/var/lib/docker...` on the actual host. To expose a directory path
on the actual host as the etcd data dir, we modify the kind config to include
```
$ cat roles/master/files/kind.yaml | grep etcd -B 3
  extraMounts:
  - containerPath: /var/lib/data
    hostPath: /data/etcd
  - containerPath: /var/wai-nfs-provisioner
    hostPath: /data/wai-nfs-provisioner
```
Mounting `/var` this way also catches nfs volumes. How to snapshot these
hostpaths is outside the scope of this document (eg: back /data by a cloud
provider storage device or archive contents of /data to s3 daily). Whichever way
we choose, we should ensure it works even when etcd is encrypted.

#### Backup/Restore

See [examples](../examples/etcd) folder for how to perform a backup/restore operation.

### NFS

See [examples](../examples/nfs) folder for details on the NFS server setup. Also
note that since an NFS server is already running on-prem, we only need the
dynamic provisioner half of the NFS setup that is currently being deployed.

## LoadBalancing

We currently run a single master. Kubectl and other API tools communicate
directly with this master. So we don't need to loadbalance requests to the
Kubernetes api server. Obviously loadbalancing services are avaible within a
cluster with the standard Kubernetes Services and Ingress.

However to expose a public IP of a Kubernetes service (eg: the Kubeflow
dashboard) - we need to expose a port on the host machine to the public. We do
this by using the `hostPort` construct on individual deployment yamls
```
$ cat ./roles/kubeflow/tasks/config.yaml | grep loadbalance -A 4
# TODO: Expose a real loadbalancer that can proxy to any service in the cluster.
- name: Expose loadbalancer on host port 80
  shell: "kubectl get deployments -n istio-system istio-ingressgateway -o json | sed 's/\"containerPort\": 80,/\"containerPort\": 80, \"hostPort\": 80,/g' | kubectl apply -f -"
  tags: [config, apply]
```
And exposing those ports through the kind config.
```
$ cat ./roles/master/files/kind.yaml | grep -i extraPort -A 12
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 8080
    hostPort: 8080
    protocol: TCP
  - containerPort: 8000
    hostPort: 8000
    protocol: TCP
```
Only the ports listed in the kind config are excluded from firewall rules, and
services listening on these ports should (typically) implement some form of
authn/authz to protect against cross namespace user meddling as well as from
external meddling from the internet (basic password auth, or more advanced OIDC
are both configurable, but these discussions are outside the scope of this
document).

NB: the idea way to do this would be to expose a loadbalancer like nginx on
ports :80 and :443 and have it route to specific Kubernetes services basis the
`Host` header in the http request.

## RBAC

### Terminology

* `ClusterRole`: A definition of what users linked to this role are allowed to do across all namespaces (i.e create, destroy pods etc)
* `User`: implemented as NS + SA {eg: admin + db-service-sa -> db service pods only allowed to access db service}

### Overview

An implementation of the rule: Kubeflow can create pipelines in any namespace but you can only view pipelines in your own namespace.
```
    ClusterRole: pipeline-runner
                |
                |
  rolebinding /  ------------------ \  clusterrolebinding
             /                       \
User SA: pipeline-runner            kubeflow SA: ml-pipeline
```
* The `pipeline-runner` ClusterRole allows all binders to access `pipeline.kubeflow.org` types.
* The `pipeline-runner` RoleBinding allows a specific SA (pipeline-runner), in one NS (admin), to access everything listed in the ClusterRole `pipeline-runner`.
* The `ml-pipeline` ClusterRoleBinding allows one SA (ml-pipeline) to access everything listed in the ClusterRole `pipeline-runner` across all NS.

An implementation of the rule: Everything I create (sa: default-editor) should be able to create workflows/pipelines (clusterRole: pipeline-runner) but those pipielines (sa: pipeline-runner-edit) should only be able to list/create pods (clusterRole: kubeflow-edit) within my own NS.
```
ClusterRole: pipeline-runner     ClusterRole: kubeflow-edit
                |                  |
                |                  |
  rolebinding /                     \  rolebinding
             /                       \
User SA: default-editor            Use SA: pipeline-runner-edit
```

## Contributing

Here are some tips for contributing ansible provisioning scripts to this repo:

* Use Ansible [facts](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variables-discovered-from-systems-facts) to determine the remote host information. For example, it can tell us whether the host is running Debian or RedHat.

* Use the [when](https://docs.ansible.com/ansible/latest/user_guide/playbooks_conditionals.html#the-when-statement) directive to conditionally enable/disable behaviors. For example, we can install different packages depends on the host OS distribution.

* Check-in YAML manifests or other configurations to the code repo instead of downloading them on the fly. This provides some level of hermeticity and reduces the chance of picking up changes that we have not tested yet.

* During prototyping phase, we will resume from a previously failed installation quite often. Tasks should be idempotent if possible. For example, `kubectl create` fails when resource already exists. Piping the output of `kubectl create ... --dry-run -o yaml` to `kubectl apply -f -` handles both create and update.

A good way to start contributing would be to find areas where the current repo
doesn't follow the guidelines, and fix it. The last rule in particular, is
violated in several places that use `kubectl apply`.

## Appendix

### Debugging

General debugging tips:
* Use `kubectl can-i`, [examples](https://www.ibm.com/docs/en/cloud-app-management/2019.4.0?topic=topics-authorizing-data-collector-access-kubernetes-resources)
```
beeps@localtoast:~$ k auth can-i list nodes -n admin --as system:serviceaccount:admin:default-editor
Warning: resource 'nodes' is not namespace scoped
no
beeps@localtoast:~$ k auth can-i list pods -n admin --as system:serviceaccount:admin:default-editor
yes
beeps@localtoast:~$ k auth can-i list workflows -n admin --as system:serviceaccount:admin:default-editor
no
```

#### KFP RCP Read errors

These errors will show up as soon as you create a Jupyter notebook and look
like:
```
Method: kfp.list_experiments()

Code: 6 (UnhandledError)
Message: (403)
Reason: Forbidden
HTTP response headers: HTTPHeaderDict({'content-length': '19', 'content-type': 'text/plain', 'date': 'Thu, 22 Apr 2021 05:54:26 GMT', 'server': 'envoy', 'x-envoy-upstream-service-time': '0'})
HTTP response body: RBAC: access denied

Details: You can find more information under /home/jovyan/kale.log
```
If you simple install a profile, you should have a namespace with the same name,
and the following service accounts
```
beeps@localtoast:~$ kp get sa
NAME             SECRETS   AGE
default          1         16h
default-editor   1         16h
default-viewer   1         16h
```
You need to create a new ServiceRoleBinding that allows RPCs to the ml-service
that's running in the kubeflow namespace.

#### In-pipeline Argo workflow errors

Within a pipeline step, the logs say
```
HTTP response body: {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"workflows.argoproj.io \"helloworld-rxr8k\" is forbidden: User \"system:serviceaccount:admin:default-editor\" cannot get resource \"workflows\" in API group \"argoproj.io\" in the namespace \"admin\"","reason":"Forbidden","details":{"name":"helloworld-rxr8k","group":"argoproj.io","kind":"workflows"},"code":403}
```
This error is fixed with the RBAC default-editor fix explained above.

#### NFS errors

Pod stuck in `ContainerCreating` with `kubectl describe` showing
```
Mounting command: mount
Mounting arguments: -t nfs 10.96.117.101:/ /var/lib/kubelet/pods/69bb0700-74df-445d-bed1-4171ec8d5a1e/volumes/kubernetes.io~nfs/nfs
Output: mount.nfs: access denied by server while mounting 10.96.117.101:/
```
Could be an nfs version issue. Try execing into the kind docker container and
manually executing the mount command, ie:
```
root@mls-control-plane:/# mount -t nfs -o hard,nfsvers=3.0 10.96.117.101:/ /tmp/foo
mount.nfs: access denied by server while mounting 10.96.117.101:/
root@mls-control-plane:/# mount -t nfs 10.96.117.101:/ /tmp/foo
root@mls-control-plane:/#
```
If that works, make sure your pv is created with the right mountOptions (i.e
remove the following lines from the pv)
```
mountOptions:
- hard
- nfsvers=3.0
```

## References

* [etcd releases](https://github.com/etcd-io/etcd/releases)
