import os
import sys
import paramiko
import logging

SSH_PORT = 22
NO_OF_RETRIES = 3
KEY_PATH = '~/.ssh/id_rsa'


class SFTPHandler(object):

    def __init__(self, host, username, password, rsa_key=KEY_PATH, port=SSH_PORT):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.rsa_key = rsa_key
        self.transport = None
        self.sftp_client = None

    def __create_sftp_client(self):
        """
        create ftp connection to remote server
        :param ip: string
        :param username: string
        :param password: string
        :return: tuple
        """
        print("Creating SFTP Client instance")
        if self.host and self.username:
            for iteration in range(1, NO_OF_RETRIES):
                try:
                    self.transport = paramiko.Transport((self.host, self.port))
                    if self.password:
                        print("Connecting to sftp host {} as {} using password".format(self.host, self.username))
                        self.transport.connect(username=self.username, password=self.password)
                    else:
                        print("Connecting to sftp {} as {} using RSA key".format(self.host, self.username))
                        self.transport.connect(username=self.username,
                                          pkey=paramiko.RSAKey.from_private_key_file(os.path.expanduser(KEY_PATH)))
                    self.sftp_client = paramiko.SFTPClient.from_transport(self.transport)
                    print("SFTP remote Connection successful")
                    return None
                except (paramiko.AuthenticationException, paramiko.BadHostKeyException, paramiko.SSHException, Exception):
                    print("Iteration {}: FTP Connection Failed to Server {1}".format(iteration, self.host))
        else:
            print("Cannot connect to remote server, either ipAddress or username is missing.")

    def __get_sftp_client(self):
        """
        Get SFTP Client
        :return:
        """
        if self.transport is None:
            self.__create_sftp_client()
        return self.sftp_client

    def upload_file(self, localfile, remotefile):
        """
        Copy a local file (localpath) to the SFTP server as remotepath
        :param localfile: the local file to copy
        :param remotefile:  the destination path on the SFTP server. Note that the filename should be included.
        Only specifying a directory may result in an error.
        :return:
        """
        sftp = self.__get_sftp_client()
        sftp.put(localfile, remotefile)
        print("File: '{}' uploaded Successfully".format(remotefile))

    def close(self):
        """
        Close the SFTP session and its underlying channel.
        :return:
        """
        print("Closing SFTP session and its underlying channel")
        self.sftp_client.close() if self.sftp_client is not None else None
        self.transport.close() if self.transport is not None else None
        print("Session closed.")


if __name__ == '__main__':
    local_path = sys.argv[1]
    sftp_info = sys.argv[2]
    remote_path = sftp_info.split(':')[-1] + "/" + local_path.split(os.sep)[-1]
    sftp_cred = sftp_info.split(':')[0]
    username = sftp_cred.split('@')[0]
    host = sftp_cred.split('@')[1]
    password = raw_input("Enter password: ")

    handler = SFTPHandler(host, username, password)
    handler.upload_file(local_path, remote_path)
