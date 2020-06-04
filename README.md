# GitPagesMirror

Mirror your GitPage by Flask.

## How To Build

* Install Python3.6+ in your machine.

* Install requirements by pip.

```bash
pip install -r requirements.txt
```

* Execute below code to add your repository mirror.

```bash
python manage.py add_repo
```

* If config this program on server, pay attention to grant file permission for runtime directory.

### Without Apache

* Execute below code just OK.

```bash
python manage.py runserver -p [port]
```

### With Apache (WSGI)

* Execute below commands To Install Apache.

```bash
# Below code just use on Ubuntu.
apt install apache2
apt install libapache2-mod-wsgi-py3
a2enmod wsgi
```

* Put Apache EnvVar Config.

```bash
# Add below code in the end of "/etc/apache2/envvars".
export LANG='en_US.UTF-8'
export LC_ALL='en_US.UTF-8'
```

* Add vHost.

```text
<VirtualHost *:80>
        ServerName example.com
        DocumentRoot /var/www/GitPagesMirror
        WSGIScriptAlias / /var/www/GitPagesMirror/wsgi.py
</VirtualHost>
```

* Put This Program To "/var/www".

### With Nginx (uWSGI)

* Add path mappings.

```text
location / {
    include uwsgi_params;
    uwsgi_pass unix:///tmp/git-pages-mirror.sock;
}
```

* Run uWSGI.

```bash
uwsgi uwsgi.ini
```
