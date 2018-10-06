import psycopg2
from json import load
from sshtunnel import SSHTunnelForwarder


class DBInterface:
    def __init__(self, settings_file: str = 'res/ssh_db_pw.json'):
        with open(settings_file, 'r', encoding='utf-8') as settings_data:
            settings = load(settings_data)
            # Remote server settings
            self.PORT = settings['SSH_TUNNEL']['PORT']
            self.REMOTE_HOST = settings['SSH_TUNNEL']['REMOTE_HOST']
            self.REMOTE_SSH_PORT = settings['SSH_TUNNEL']['REMOTE_SSH_PORT']
            self.REMOTE_USERNAME = settings['SSH_TUNNEL']['REMOTE_USERNAME']
            self.REMOTE_PASSWORD = settings['SSH_TUNNEL']['REMOTE_PASSWORD']

            # Database settings
            self.DB_NAME = settings['DATABASE']['DB_NAME']
            self.DB_USER = settings['DATABASE']['DB_USER']
            self.DB_HOST = settings['DATABASE']['DB_HOST']
            self.DB_PASS = settings['DATABASE']['DB_PASS']

        # Setup ssh vpn tunnel
        self.ssh_tunnel = SSHTunnelForwarder((self.REMOTE_HOST, self.REMOTE_SSH_PORT),
                                             ssh_username=self.REMOTE_USERNAME,
                                             ssh_password=self.REMOTE_PASSWORD,
                                             remote_bind_address=('localhost', self.PORT),
                                             local_bind_address=('localhost', self.PORT))
        self.ssh_tunnel.start()

    def __str__(self):
        if self.ssh_tunnel.is_active:
            return f'DBInterface object connected via ssh tunnel to {self.REMOTE_HOST} on local port {self.PORT}'
        else:
            return 'DBInterface object not currently connected to a tunnel'

    def close(self):
        """
        Must be called before exiting
        """
        self.ssh_tunnel.close()

    def run_command(self, command_string: str, args_tuple: tuple = None):
        """
        Runs a SQL command on the remote server over an SSH VPN tunnel
        :param command_string: SQL command string to run
        :param args_tuple: tuple of parameter values to use in command string
        :return: cursor object with data gathered from database
        """
        try:
            conn = psycopg2.connect(
                database=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASS,
                host=self.ssh_tunnel.local_bind_host,
                port=self.ssh_tunnel.local_bind_port,
            )
        except Exception as e:
            print(f'Unable to connect to the database: {e}')
        else:
            cursor = conn.cursor()
            if args_tuple is not None:
                cursor.execute(command_string, args_tuple)
            else:
                cursor.execute(command_string)

            return cursor.fetchall()
