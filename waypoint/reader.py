"""
Code related to a reader profile
"""
import json

from waypoint.core import FestivalTagReader
from waypoint.core import Logger
from waypoint.analysis import TagStreamEvent
from waypoint.actuator import Actuator
from Kamaelia.Chassis.ConnectedServer import FastRestartServer
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.PAR import PAR
from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Util.Backplane import *
from Kamaelia.Util.Console import ConsoleEchoer
from Kamaelia.Util.PureTransformer import PureTransformer

def DebugTapProtocol(**args):
    return SubscribeTo("TAGS")

def ActuatorTriggerProtocol(**args):
    return PublishTo("ACTUATE")

def ActuatorTriggerTapProtocol(**args):
    return Pipeline(
        SubscribeTo("ACTUATE"),
        PureTransformer(lambda x: json.dumps(x) + "\n")
        )


def TagReaderClient(collator_ip="127.0.0.1",
                    collator_port=1600,
                    node_id=1,
                    logfile="tagsread.log",
                    debug_port=1500,
                    actuator_port=1600,
                    actuator_tap_port=1700):

    # Use the PAR component to allow deferred activation, and to allow the components
    # to be used as a unit.

    return PAR(
                Backplane("TAGS"),
                Backplane("ACTUATE"),

                Pipeline(
                    FestivalTagReader(node_id),   # FIXME: Probably don't want json encoding in here
                    PublishTo("TAGS")
                ),

                FastRestartServer(protocol=DebugTapProtocol, port=debug_port),
                FastRestartServer(protocol=ActuatorTriggerProtocol, port=actuator_port),
                FastRestartServer(protocol=ActuatorTriggerTapProtocol, port=actuator_tap_port),

                # Connect to Collator
#                Pipeline(
#                    SubscribeTo("TAGS"),
#                    TCPClient(collator_ip,collator_port)
#                ),
                Pipeline(
                    SubscribeTo("TAGS"),
                    PureTransformer(lambda x: x[:-1]), # Strip trailing /n
                    Logger(logfile=logfile),
                ),

                Pipeline(
                    SubscribeTo("TAGS"),
                    PureTransformer(lambda x: x[:-1]),         # Strip trailing /n
                    PureTransformer(lambda x: json.loads(x) ), # Restore record
                    TagStreamEvent(temporal_separation=0.5),   # Extract tag taps
                    PublishTo("ACTUATE"),
                ),

                Pipeline(
                    SubscribeTo("ACTUATE"),
                    Actuator()
                ),

                # For debugging purposes
                Pipeline(
                    SubscribeTo("TAGS"),
                    ConsoleEchoer()
                ),
              )
