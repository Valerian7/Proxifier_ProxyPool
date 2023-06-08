# Proxifier_ProxyPool
Proxifier批量添加代理服务器

- 自动检测可用的代理
- 批量添加代理服务器


## 使用说明
提供代理列表文件，每行一个
```console
usage: Proxifier_ProxyPool.py [-h] [-f FILE] [-o OUTPUT] [-c CHECK]

python3 Proxifier_ProxyPool.py -f proxy_list.txt -o test.ppx -c http://baidu.com

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  指定要打开的代理列表文件，每行一个
  -o OUTPUT, --output OUTPUT
                        输出新的配置文件名称，默认:NewProxifierConfig.ppx
  -c CHECK, --check CHECK
                        指定验证代理网址，默认:https://baidu.com
```

## 使用效果

![image](https://github.com/Valerian7/Proxifier_ProxyPool/assets/46412054/22661a88-c548-43ff-ab5f-977bd8ee0f41)
