from pykube.config import KubeConfig
from pykube.http import HTTPClient
import json
import etcd
from gluster import gfapi

kubeconfig = KubeConfig('kubeconfig')


class Pod(object):
    def __init__(self):
        self.client = HTTPClient(kubeconfig)

    def pod_view(self, pod_name):
        url = "namespaces/default/pods"
        pods = json.loads(self.client.get(url=url).content)['items']
        for pod in pods:
            if pod['metadata']['labels']['run'] == pod_name:
                return pod
        return None

    def delete_pod(self, name):
        url = "namespaces/default/pods"
        pods = json.loads(self.client.get(url=url).content)['items']
        for pod in pods:
            if pod['metadata']['labels']['run'] == name:
                pod_name = pod['metadata']['name']
                del_url = "namespaces/default/pods/{}".format(pod_name)
                delete_result = self.client.delete(url=del_url).content
                return delete_result
        return None


class ReplicationController(object):
    def __init__(self):
        self.client = HTTPClient(kubeconfig)

    def create_replication_controller(self, name, replicas):
        volume_gfs_name = "vol-{}".format(name)
        host_path_mount = "/mnt/{}".format(name)
        volumemount = {'name': volume_gfs_name, 'mountPath': '/apps'}
        volumemounts = [volumemount]
        container_atom = {'name': name,
                          'image': "registry.baijiahulian.com/atom",
                          'ports': [{'containerPort': 22}],
                          'imagePullPolicy': 'Always',
                          'volumeMounts': volumemounts,
                          'dnsPolicy': 'Default',
                          'resources': {'limits': {'cpu': '500m',
                                                   'memory': '2000Mi'},
                                        'requests': {'cpu': '10m',
                                                     'memory': '512Mi'}}}
        containers = list()
        containers.append(container_atom)
        volume_gfs = {'name': volume_gfs_name,
                      'hostPath': {'path': host_path_mount}}
        volumes = list()
        volumes.append(volume_gfs)
        podtemplatespec = dict()
        podtemplatespec['metadata'] = {}
        podtemplatespec['metadata']['name'] = name
        podtemplatespec['metadata']['labels'] = {"run": name}
        podtemplatespec['spec'] = {}
        podtemplatespec['spec']['containers'] = containers
        podtemplatespec['spec']['volumes'] = volumes
        body = dict()
        body["kind"] = "ReplicationController"
        body["apiVersion"] = "v1"
        body["metadata"] = {"name": name}
        body["spec"] = {"replicas": replicas, "template": podtemplatespec}
        data = json.dumps(body)
        replicationcontroller = json.loads(
            self.client.post(url="namespaces/default/replicationcontrollers",
                             data=data).content)
        return replicationcontroller

    def delete_replication_controller(self, name):
        rc_path = "namespaces/{}/replicationcontrollers/{}".format("default",
                                                                   name)
        body = {"gracePeriodSeconds": 0}
        data = json.dumps(body)
        delete_result = json.loads(self.client.delete(url=rc_path,
                                                      data=data).content)
        return delete_result


class Service(object):
    def __init__(self):
        self.client = HTTPClient(kubeconfig)

    def create_service(self, name):
        ports = list()
        port_22 = {"name": "ssh", "port": 22}
        port_80 = {"name": "http", "port": 80}
        port_443 = {"name": "https", "port": 443}
        ports.append(port_22)
        ports.append(port_80)
        ports.append(port_443)
        #for portNum in range(7000,7010):
        #    port_custom = {"name": portNum, "port": portNum}
        #    ports.append(port_custom)
        body = dict()
        body["kind"] = "Service"
        body["apiVersion"] = "v1"
        body["metadata"] = {"name": name}
        body["spec"] = {"selector": {"run": name}, "type": "NodePort"}
        body["spec"]["ports"] = ports
        data = json.dumps(body)
        service = json.loads(
            self.client.post(url="namespaces/default/services",
                             data=data).content)
        return service

    def view_service(self, name):
        url = "namespaces/{}/services/{}".format("default", name)
        service = json.loads(self.client.get(url=url).content)
        return service

    def delete_service(self, name):
        service_path = "namespaces/{}/services/{}".format("default", name)
        body = {"gracePeriodSeconds": 0}
        data = json.dumps(body)
        delete_result = json.loads(self.client.delete(url=service_path,
                                                      data=data).content)
        return delete_result


class Etcd(object):
    def __init__(self):
        self.namespace = "default"
        self.etcd_client = etcd.Client(host='192.168.47.151', port=2379)

    def add_web_app(self, name, namespace, http_port, https_port, host_ip):
        domain = "{}.ctest.baijiahulian.com {}.ctest.genshuixue.com".format(
            name, name)
        app = "devnginx/{}/{}".format(namespace, name)
        app_info = {"name": name,
                    "http_port": http_port,
                    "https_port": https_port,
                    "domain": domain,
                    "host_ip": host_ip}
        self.etcd_client.set(app, json.dumps(app_info))

    def del_web_app(self, name, namespace):
        app = "devnginx/{}/{}".format(namespace, name)
        self.etcd_client.delete(app)


class GFS(object):
    def __init__(self):
        self.volume = gfapi.Volume("192.168.47.151", "gv0")
        self.volume.mount()

    def create_dir(self, name):
        self.volume.mkdir(name, 0755)
        self.volume.umount()
