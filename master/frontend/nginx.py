import os

def reload_nginx():
    try:
        os.system("sudo ./reload_nginx.sh")

    except:
        print("Unable to reload nginx!");

    else:
        print("nginx realoded successfully!");
    

def create_config_file(subdomain, port):
    file_name = "/etc/nginx/sites-enabled/" +  subdomain + ".conf"
    f = open(file_name, "w")

    configuration ='''server {{
        listen 80;
        server_name {0}.hoster.local;

        location / {{
                proxy_pass http://192.168.196.125:{1};
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
        }}

}}
    '''.format(subdomain, port);
    f.write(configuration);
    f.close();

    reload_nginx();







