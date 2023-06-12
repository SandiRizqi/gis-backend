import ee
import datetime
from turfpy.measurement import area
import json
from decouple import Config, RepositoryEnv
import argparse

parser = argparse.ArgumentParser()


parser.add_argument("-env", "--env", action="env")
args = parser.parse_args()


def init():
    service_account = 'earth-engine@geocircle-512f9.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './geocircle-512f9-6640610a0602.json')
    ee.Initialize(credentials)
    print("Initialized")
init()



print(args.env)

