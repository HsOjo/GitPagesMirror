# GitPagesMirror

使用 Flask 实现你的 GitPage 的镜像。

## 如何构建

* 在你的机器上安装 Python 3.6 或以上版本。

* 使用 pip 安装相关依赖。

```bash
pip install -r requirements.txt
```

* 执行以下命令以添加你的仓库镜像。

```bash
python manage.py add_repo
```

* 如果在服务器中配置，注意要为运行目录设置文件权限。

### 不使用 Apache

* 执行以下命令即可。

```bash
python manage.py runserver -p [port]
```

### 使用 Apache (WSGI)

* 执行以下代码安装 Apache。

```bash
# Below code just use on Ubuntu.
apt install apache2
apt install libapache2-mod-wsgi-py3
a2enmod wsgi
```

* 添加 Apache 环境变量设置。

```bash
# Add below code in the end of "/etc/apache2/envvars".
export LANG='en_US.UTF-8'
export LC_ALL='en_US.UTF-8'
```

* 添加虚拟主机。

```text
<VirtualHost *:80>
        ServerName example.com
        DocumentRoot /var/www/GitPagesMirror
        WSGIScriptAlias / /var/www/GitPagesMirror/wsgi.py
</VirtualHost>
```

* 将这个程序放到 "/var/www"。

### 使用 Nginx (uWSGI)

* 添加路径映射。

```text
location / {
    include uwsgi_params;
    uwsgi_pass unix:///tmp/git-pages-mirror.sock;
}
```

* 启动uWSGI。

```bash
uwsgi uwsgi.ini
```
