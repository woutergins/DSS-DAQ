# import logging
# logging.basicConfig(level=logging.INFO)
# from suds import wsdl
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
from suds.client import Client
import os

url = r"http://npg.dl.ac.uk/MIDAS/DataAcq/DataBase/DataBaseAccess.wsdl"
location = os.getcwd() + '/midas.wsdl'
client = Client(url, location=location)
print(client)
