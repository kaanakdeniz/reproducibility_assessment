import configparser

config = configparser.ConfigParser()
config.read('config.ini')

GITHUB_API_TOKEN = config["GITHUB_API"]["token"]
