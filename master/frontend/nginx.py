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



def create_load_balanced_config(subdomain, port1, port2):
    print("LOAD BALANCE CONFIG")

    file_name = "/etc/nginx/sites-enabled/" +  subdomain + ".conf"
    f = open(file_name, "w")

    configuration ='''upstream {0}_nginx {{
    server 192.168.196.125:{1};
    server 192.168.196.27:{2};
}}
# This server accepts all traffic to port 80 and passes it to the upstream.
server {{
        listen 80;
        server_name {0}.hoster.local;
        location / {{
            proxy_pass http://{0}_nginx;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
}}
    '''.format(subdomain, port1, port2);
    f.write(configuration);
    f.close();

    reload_nginx();





create_load_balanced_config("flask_yo1", "9999", "9991");
