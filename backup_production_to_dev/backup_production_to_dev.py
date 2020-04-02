mport os
import subprocess
from django.conf import settings
from django.core.management import BaseCommand
from django_secrets import AWSSecretsManagerSecrets
def run(cmd, env=None, **kwargs):
    print(cmd)
    env = env or {}
    return subprocess.run(cmd, shell=True, env=dict(os.environ, **env), **kwargs)
CASE_DUMP = 'dump'
CASE_RESTORE = 'restore'
FILENAME = 'dump.sql'
dump_dir = os.path.join(settings.ROOT_DIR, '.dump')
os.makedirs(dump_dir, exist_ok=True)
DB_DUMP_FILEPATH = os.path.join(dump_dir, FILENAME)
class Command(BaseCommand):
    @staticmethod
    def _db_cmd(db_info, case):
        host = db_info['HOST']
        port = db_info['PORT']
        db = db_info['NAME']
        user = db_info['USER']
        password = db_info['PASSWORD']
        if case == CASE_DUMP:
            run(f'pg_dump -h {host} -Fc {db} -U {user} > {DB_DUMP_FILEPATH}', env={'PGPASSWORD': password}, check=True)
        elif case == CASE_RESTORE:
            run(f'dropdb -h {host} -U {user} {db}', env={'PGPASSWORD': password}, check=True)
            run(f'createdb -h {host} -U {user} -T template0 -l C -e {db}', env={'PGPASSWORD': password}, check=True)
            run(f'pg_restore -h {host} -d {db} -U {user} {DB_DUMP_FILEPATH}', env={'PGPASSWORD': password}, check=True)
    @staticmethod
    def _storage_cmd(storage_info, case):
        pass
    def handle(self, *args, **options):
        # production, dev환경의 비밀 값 가져오기
        secrets_production = AWSSecretsManagerSecrets('config.settings.production')
        secrets_dev = AWSSecretsManagerSecrets('config.settings.dev')
        # production, dev의 DB설정 가져오기
        db_production = secrets_production['DATABASES']['default']
        db_dev = secrets_dev['DATABASES']['default']
        db_local = {**db_dev, 'HOST': 'localhost'}
        try:
            # production에서 DB dump해와서 dev에 load
            self._db_cmd(db_production, CASE_DUMP)
            self._db_cmd(db_dev, CASE_RESTORE)
            self._db_cmd(db_local, CASE_RESTORE)
        finally:
            try:
                os.remove(DB_DUMP_FILEPATH)
            except OSError:
                pass
