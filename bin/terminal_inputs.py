import argparse


def terminal_inputs():
    """Parse the terminal inputs and return the arguments"""

    parser = argparse.ArgumentParser(
        prog="keelson-connector-lidar-yd",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log-level",
        type=int,
        default=30,
        help="Log level 10=DEBUG, 20=INFO, 30=WARN, 40=ERROR, 50=CRITICAL 0=NOTSET",
    )
    parser.add_argument(
        "--connect",
        action="append",
        type=str,
        help="Endpoints to connect to, in case multicast is not working.",
    )
    parser.add_argument(
        "-r",
        "--realm",
        type=str,
        required=True,
        help="Unique id for a domain/realm to connect",
    )
    parser.add_argument(
        "-e",
        "--entity-id",
        type=str,
        required=True,
        help="Unique id for a entity to connect",
    )
    parser.add_argument(
        "-dp",
        "--device-port",
        type=str,
        required=True,
        help="Device connection PORT string for Ex. Linux: /dev/ttyACM0 or Windows: COM3",
    )

    ## Parse arguments and start doing our thing
    args = parser.parse_args()

    return args
