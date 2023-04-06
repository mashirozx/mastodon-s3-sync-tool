import configparser
from os import path, environ
from json import dumps as JSONDumps

project_dir = path.dirname(path.abspath(__file__))
private_dir = path.join(project_dir, '../../private')
tmp_dir = path.join(project_dir, '../../tmp')

config_file_name = environ.get('CONFIG_FILE_NAME', 'config.ini')

config_file_path = path.join(private_dir, config_file_name)

config = configparser.ConfigParser()
config.read(config_file_path)

s3_source_access_key = config['s3.source']['access_key']
s3_source_secret_key = config['s3.source']['secret_key']
s3_source_endpoint_url = config['s3.source']['endpoint_url']
s3_source_bucket = config['s3.source']['bucket']

s3_destination_access_key = config['s3.destination']['access_key']
s3_destination_secret_key = config['s3.destination']['secret_key']
s3_destination_endpoint_url = config['s3.destination']['endpoint_url']
s3_destination_bucket = config['s3.destination']['bucket']

pg_tunnel_enabled = config['pg.tunnel']['enabled']
pg_tunnel_ssh_host = config['pg.tunnel']['ssh_host']
pg_tunnel_ssh_port = int(config['pg.tunnel']['ssh_port'])
pg_tunnel_ssh_user = config['pg.tunnel']['ssh_user']
pg_tunnel_ssh_password = config['pg.tunnel']['ssh_password']
_pg_tunnel_ssh_key = config['pg.tunnel']['ssh_key']
pg_tunnel_ssh_key = path.join(
    private_dir, _pg_tunnel_ssh_key) if _pg_tunnel_ssh_key else None
pg_tunnel_local_host = config['pg.tunnel']['local_host']
pg_tunnel_local_port = int(config['pg.tunnel']['local_port'])

pg_db_host = config['pg.database']['host']
pg_db_port = int(config['pg.database']['port'])
pg_db_user = config['pg.database']['user']
pg_db_password = config['pg.database']['password']
pg_db_database = config['pg.database']['database']

celery_broker = config['celery']['broker']
celery_backend = config['celery']['backend']
celery_log_level = config['celery']['log_level']
celery_concurrency = int(config['celery']['concurrency'])

if __name__ == '__main__':
    config_dict = {
        section: dict(config[section])
        for section in config.sections()
    }
    print(JSONDumps(config_dict, indent=4))
    print(pg_tunnel_ssh_key)
