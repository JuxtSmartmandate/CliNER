
import os
import subprocess
import signal
import atexit
from cliner.lib.java.entry_point.get_py4j_dir import get_py4j_dir


gateway_runner = os.environ["CLINER_DIR"] + \
    "/cliner/lib/java/entry_point/runner.sh"

# dependencies
JAVA_DIR = os.path.join(*[os.environ["CLINER_DIR"], "cliner", "lib", "java"])
METAMAP_DIR = os.path.join(JAVA_DIR, "metamap")
LVG_DIR = os.path.join(JAVA_DIR, "lvg_norm")
STANFORD_DIR = os.path.join(JAVA_DIR, "stanford_nlp")
ENTRY_POINT_DIR = os.path.join(JAVA_DIR, "entry_point")

STANFORD_DEPENDENCIES = ":{}:{}".format(os.path.join(
    *[STANFORD_DIR, "stanford-corenlp-full", "*"]), STANFORD_DIR)
NORMAPI_DEPENDENCIES = ":{}:{}".format(
    os.path.join(*[LVG_DIR, "lvg", "lib", "*"]), LVG_DIR)
METAMAP_DEPENDENCIES = ":{}:{}".format(METAMAP_DIR, os.path.join(
    *[METAMAP_DIR, "metamapBase", "public_mm", "src", "javaapi", "dist", "*"]))
PY4J_DEPENDENCIES = ":{}".format(
    os.path.join(get_py4j_dir(), "*"))
ENTRY_POINT_DEPENDENCIES = ":{}".format(os.path.join(ENTRY_POINT_DIR, "*"))

DEPENDENCIES = ENTRY_POINT_DIR + PY4J_DEPENDENCIES + \
    METAMAP_DEPENDENCIES + NORMAPI_DEPENDENCIES + STANFORD_DEPENDENCIES

devnull = open(os.devnull, "wb")


class GateWayServer(object):
    """
        creates the py4j gateway to allow access to jvm objects.
        only one gateway server may be running at a time on a specific port.
    """

    server = None

    def __init__(self):
        pass

    @staticmethod
    def launch_gateway():

        if GateWayServer.server is None:
            GateWayServer.server = subprocess.Popen(
                ["java", "-cp", DEPENDENCIES, "gateway.GateWay"], stdout=devnull, stderr=subprocess.STDOUT)

    @staticmethod
    @atexit.register
    def cleanup():

        print("Cleanup entered")
        if GateWayServer.server is not None:
            os.kill(GateWayServer.server.pid, signal.SIGKILL)
            from IPython.core.debugger import Tracer  # NOQA
            Tracer()()
            GateWayServer.server = None
            devnull.close()
        print("Cleanup exited.")

    def __del__(self):
        pass

if __name__ == "__main__":

    print("nothing to do in main")
    GateWayServer.launch_gateway()

    while True:
        pass
