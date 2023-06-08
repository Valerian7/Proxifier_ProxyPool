import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from concurrent.futures import ThreadPoolExecutor
import re
import argparse
import requests


proxies_list = []

#筛选可用的代理
def check(proxy_url,check_url):
    try:
        parsed_proxy = proxy_url.split("://")
        scheme = parsed_proxy[0]
        auth_and_address = parsed_proxy[1].split('@')
        if len(auth_and_address) == 2:
            auth, address = auth_and_address
            proxy = {
                scheme: f"{scheme}://{auth}@{address}",
                "https": f"{scheme}://{auth}@{address}"
            }
        else:
            address = auth_and_address[0]
            proxy = {
                scheme: f"{scheme}://{address}",
                "https": f"{scheme}://{address}"
            }
        rsp = requests.get(check_url, proxies=proxy, timeout=5)
        if rsp.status_code == 200:
            print(f"\033[32m Success\033[0m：{proxy_url}")
            with open('proxy_success.txt', 'a') as f:
                f.write(proxy_url + "\n")
            parse_proxy_line(proxy_url)
    except Exception as e:
        print(f"\033[31m failure\033[0m：{proxy_url}")

#将代理协议、用户名、密码等信息提取
def parse_proxy_line(line):
    pattern = re.compile(r'^(?P<protocol>socks5|http|https)://(?:((?P<username>[^:]+):(?P<password>[^@]+))@)?(?P<ip>[^:]+):(?P<port>\d+)$')
    match = pattern.match(line)
    if not match:
        return None
    proxies_list.append(match.groupdict())

#根据模板文件生成新的配置文件
def create_proxifier_config(ProxifierConfig_name):
    with open("Demo_ProxifierConfig.ppx", "r") as f:
        existing_config = f.read()
    tree = ET.ElementTree(ET.fromstring(existing_config))
    root = tree.getroot()

    proxy_list = root.find('ProxyList')
    chain_list = root.find('ChainList')
    chain = chain_list.find("./Chain[@id='100']")

    # 根据现有的代理ID生成新的ID
    existing_ids = [int(proxy.get('id')) for proxy in proxy_list.findall('Proxy')]
    next_id = max(existing_ids) + 1

    # 添加新的代理，从列表中提取账号、密码等信息
    for proxy in proxies_list:
        proxy_element = ET.SubElement(proxy_list, "Proxy", {
            "id": str(next_id),
            "type": proxy['protocol'].upper()
        })

        if proxy['username'] and proxy['password']:
            authentication = ET.SubElement(proxy_element, "Authentication", {"enabled": "true"})
            ET.SubElement(authentication, "Password").text = proxy['password']
            ET.SubElement(authentication, "Username").text = proxy['username']

        ET.SubElement(proxy_element, "Options").text = "48" if proxy['protocol'].lower() == 'socks5' else "50"
        ET.SubElement(proxy_element, "Port").text = proxy['port']
        ET.SubElement(proxy_element, "Address").text = proxy['ip']

        chain_proxy = ET.SubElement(chain, "Proxy", {"enabled": "true"})
        chain_proxy.text = str(next_id)

        next_id += 1

    config_xml =  minidom.parseString(ET.tostring(root, encoding="utf-8", method="xml")).toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")
    config_xml = re.sub(r'\n\s*\n', '\n', config_xml)
    with open(ProxifierConfig_name, "w") as f:
        f.write(config_xml)
    print(f"\n新的Proxifier配置文件已生成：{ProxifierConfig_name}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="python3 Proxifier_ProxyPool.py -f proxy_list.txt -o test.ppx -c https://baidu.com")
    parser.add_argument("-f", "--file", help="指定要打开的代理列表文件，每行一个")
    parser.add_argument("-o", "--output", help="输出新的配置文件名称，默认:NewProxifierConfig.ppx",default="New_ProxifierConfig.ppx")
    parser.add_argument("-c", "--check", help="指定验证代理网址，默认:https://baidu.com",default="https://baidu.com")
    args = parser.parse_args()

    if args.file is not None:
        with open(args.file, 'r',encoding="utf-8") as f:
            proxy_list = [line.strip() for line in f.readlines()]
        with ThreadPoolExecutor(max_workers=50) as m:
            for proxy_url in proxy_list:
                m.submit(check, proxy_url,args.check)
        print("\n可用代理已输出至：proxy_success.txt")
        create_proxifier_config(args.output)
