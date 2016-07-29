from pykube.config import KubeConfig
from pykube.http import HTTPClient
import json
import yaml
import etcd
import argparse

parser = argparse.ArgumentParser(description='test argparse')


kubeconfig = KubeConfig('/Users/Truman/project/kubeapi/kubeconfig')

etcd_client = etcd.Client(host='172.21.133.1',port=4001)
#etcd_client.set('/test/k1','v1')
#etcd_client.set('/test/k1','v2')
value = {"domain": "cool.ctest.baijiahulian.com cool.ctest.genshuixue.com", "http_port": 32104,
         "name": "cool", "host_ip": "172.21.133.6", "https_port": 31087, "testkey": 1}
etcd_client.set('/devnginx/default/cool',value)
print((etcd_client.delete('/devnginx/default/cool')))
#etcd_client.delete('/test/k1')
#print(etcd_client.get('/test/k1'))

#directory = etcd_client.get('/test/k1')
#for result in directory.children:
#    print(result.key + ":" +result.value)



#with open('kubeconfig') as f:
#    doc = yaml.safe_load(f.read())
#    print doc
#client = HTTPClient(kubeconfig)
#print client.get(url="pods").content
#print client.delete(url="namespaces/default/pods/natomglusterfs").content
#body={}
#body["kind"] = "Pod"
#body["apiVersion"] = "v1"
#body["metadata"] = {}
#body["metadata"]["name"] = "testmetadataname"
#body["spec"] = {}
#containers = []
#container = {}
#container['name'] = 'testname'
#container['image'] = 'atom'
#container['imagePullPolicy'] = 'IfNotPresent'
#containers.append(container)
#body["spec"]["containers"] = containers
#print json.dumps(body)
#data = json.dumps(body)
#print client.post(url="namespaces/default/pods",data=data).content
