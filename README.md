# LinkedInDog
## 简介
自动化搜索并爬取领英个人简介,通过网页另存为的方式保存.
## 使用方法
```
Usage: LinkedInDog.py crawl [OPTIONS]
Options:
  --user TEXT            领英用户名
  --pwd TEXT             领英密码
  --keywords TEXT        需要搜索的人名,公司名等
  --browser TEXT         使用的浏览器(Firefox或Chrome)
  --profile TEXT         浏览器配置路径
  --sources INTEGER      0: 仅通过领英搜索
                         1: 仅通过百度搜索
                         2: 通过领英和百度搜索
  --linkedinnum INTEGER  需要爬取的领英搜索页面数量
  --num INTEGER          需要爬取的百度搜索页面数量

```
## 注意事项
使用前需安装依赖
`pip install -r requirements.txt`
**
浏览器,selenium,geckodriver三者版本需要互相匹配.
已知可用版本套餐如下:
Firefox 52.7.3
selenium 3.3.1
geckodriver 0.15.0
**
建议在虚拟机中运行,不妨碍主机操作

