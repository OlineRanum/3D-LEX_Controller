from __future__ import print_function
from vicon_dssdk import ViconDataStream
import argparse
import sys

class ViconController:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('host', nargs='?', help="Host name, in the format of server:port", default = "localhost:801")
        args = parser.parse_args()
        print('Vicon Import OK')   

        client = ViconDataStream.Client()
        frames = []
        
        print( 'Connecting' )
        while not client.IsConnected():
            print( '.' )
            client.Connect( 'localhost:801' )
        
        try:
            while client.IsConnected():
                if client.GetFrame():
                    #store data here
                    frames.append(client.GetFrameNumber() )
        
        except ViconDataStream.DataStreamException as e:
            print( 'Error', e )
        
        return frames