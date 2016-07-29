#coding = utf-8
import argparse
import sys
import etcd
import json

parser = argparse.ArgumentParser(description="nginx 转发添加")
parser.add_argument('--namespace', help='项目所在命名空间', type=str, default='default')
parser.add_argument('--name', help='项目名字', type=str, default='default')
parser.add_argument('--location_pass', help='代理路径', type=str, default='default')

def main():
    etcd_client = etcd.Client(host='172.21.133.1', port=4001)
    args = parser.parse_args()
    print(args.namespace)
    print(add_web_app_location_pass(etcd_client, args.namespace, args.name, args.location_pass))
    return 0

def add_web_app_location_pass(etcd_client, namespace, name, location_pass):
    app_info = get_web_app(etcd_client, namespace, name)
    app_info = app_info.replace("'", "\"")
    app_info = json.loads(app_info)
    if app_info.has_key('location_pass'):
        app_info['location_pass'].append(location_pass)
    else:
        app_info['location_pass'] = []
        app_info['location_pass'].append(location_pass)
    #etcd_client.set(app, json.dumps(app_info))

def get_web_app(etcd_client, namespace, name):
    app = "devnginx/{}/{}".format(namespace, name)
    return etcd_client.get(app).value

if __name__ == "__main__":
    sys.exit(main())