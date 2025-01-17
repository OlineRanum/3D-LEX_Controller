"""Utility functions for API sample scripts."""
from __future__ import print_function
import argparse
from datetime import datetime, timedelta
import functools
import threading
import time
import traceback

import sys
# sys.path.append(r"C:\Program Files\Vicon\ShogunLive1.14\SDK\Python\vicon_core_api")

# from vicon_core_api import Client, Result, RPCError


class SampleArgumentParser(argparse.ArgumentParser):
    """Command line argument parser for sample scripts."""

    def __init__(self, *args, **kwargs):
        """Initialize with common arguments."""
        super(SampleArgumentParser, self).__init__(*args, **kwargs)
        # All samples need to connect to the application instance, this can be on the local host machine or a remote host machine.
        self.add_argument('--host', help="Terminal server host IP address", default="localhost", type=str)
        # The default port for the Vicon Core API server is 52800. This can be changed by supplying a command line argument when starting the application:
        # Tracker4.exe --terminal-port=52801
        self.add_argument('--port', help="Terminal server port", default=52800, type=int)


class PersistentClientConnection(object):
    """Base class for sample scripts that try to remain connected to the application until the user presses the 'X' key."""
    
    def __init__(self, host, port):
        """Initialize with IP address for the application."""
        self.host = host
        self.port = port
        self.client = None
        self.exit = False

    def connect(self):
        """Connect to the application, and call client_handler_function when a new connection is established."""
        thread = None
        while not self.exit:
            try:
                print("Connecting to {}:{}...".format(self.host, self.port))
                try:
                    client = Client(self.host, self.port)
                    if not client.connected:
                        time.sleep(2)
                        continue

                    thread = threading.Thread(target=functools.partial(self.handler_thread, client))
                    thread.start()

                    # Start keyboard handling loop.
                    while not self.exit:
                        key_char = get_standard_key().decode("utf-8")
                        if key_char == 'x':
                            self.exit = True
                            break
                        self.handle_key_press(key_char)
                finally:
                    # Stopping the client will cause an RPCNotConnected error in the monitor, which allows us to join the thread.
                    client.stop()
                    if thread:
                        thread.join()
                        thread = None
            except RPCError as error:
                if str(error).startswith("RPCNotConnected"):
                    traceback.print_exc()
                    time.sleep(2)
                    continue
                raise

    def handler_thread(self, client):
        """Note that this function runs in a new thread."""
        try:
            self.handle_client_connection(client)
        except RPCError as error:
            # Ignore disconnected errors, we will try to reconnect unless x key was pressed.
            if not str(error).startswith("RPCNotConnected"):
                raise
        except Exception:
            # Some other fatal error, prompt user to press a key so we can join the keyboard monitoring thread.
            self.exit = True
            print("Press any key to continue...")
            raise

    def handle_client_connection(self, client):
        """Derived classes should override this function to do something with the new client connection."""
        pass

    def handle_key_press(self, key_char):
        """Derived classes can override this function to handle any additional keyboard input."""
        pass


class WaitForChangeTimeoutError(Exception):
    """Error raised when finish predicate is not satisfied before the timeout expires."""


class WaitForChange(object):
    """Helper for waiting on an API change callback."""

    def __init__(self, api_services, add_callback_function, timeout_seconds, finish_predicate=None):
        """Create monitor for API changes.
        Args:
            api_services < vicon_core_api.ViconInterface >: Vicon Core API services class.
            add_callback_function < function >: Add callback function on services class.
            timeout_seconds < float >: Timeout after this many seconds if the finish predicate is not satisfied.
            finish_predicate < function >: Callback handling function. See API callback documentation for required arguments.
                                           Return True from this function to finish waiting, or False to continue waiting.
                                           If no predicate is supplied, we will finish waiting as soon as the first callback is received).
        """
        self.api_services = api_services
        self.add_callback_function = add_callback_function
        self.timeout_seconds = timeout_seconds
        self.finish_predicate = finish_predicate if finish_predicate else self._default_finish_predicate
        self.notify_count = 0
        self.change_condition = threading.Condition()
        self.callback_id = None
        self.latest_change_args = None

    def __enter__(self):
        """Connect handler function to callback."""
        self.callback_id = check_api_call(self.add_callback_function(self._on_changed))
        return self

    def __exit__(self, _type, _value, _traceback):
        """Wait for finish predicate to return True or timeout."""

        # If an exception was raised by the calling block, re-raise it
        if _type:
            return

        try:
            deadline_time = datetime.now() + timedelta(seconds=self.timeout_seconds)
            while True:
                with self.change_condition:
                    # Check the predicate.
                    if self.latest_change_args and self.finish_predicate(*self.latest_change_args):
                        return
                    # Wait for another change callback.
                    self.change_condition.wait((deadline_time - datetime.now()).total_seconds())
                    if datetime.now() >= deadline_time:
                        raise WaitForChangeTimeoutError("Finish predicate not satisfied after {} callbacks.".format(self.notify_count))
        finally:
            # Ensure we remove the callback when finished (or timed out).
            if self.callback_id:
                check_api_call(self.api_services.remove_callback(self.callback_id))

    def _default_finish_predicate(self, *_args):
        """Default implementation of finish predicate. Finishes as soon as we receive a change callback."""
        with self.change_condition:
            return self.notify_count > 0

    def _on_changed(self, *args):
        """Notify there's been a change - we need to check if the finish predicate is satisfied.
        Note that this is called on the client receive thread, it is not safe to call any API functions here.
        Instead, we signal a change condition which is picked up on the waiting thread."""
        with self.change_condition:
            self.notify_count += 1
            self.latest_change_args = args
            self.change_condition.notify_all()


class ScopedCallback(object):
    """Helper class to remove callback on exit from the runtime context."""

    def __init__(self, services, add_callback_function, handler_function):
        self.services = services
        self.callback_id = check_api_call(add_callback_function(handler_function))

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        if self.callback_id:
            self.services.remove_callback(self.callback_id)


class DeviceDeltaHelper(object):
    """Helper for maintaining a dictionary of device URNs and values with a delta update function."""

    def __init__(self, delta_function):
        self.delta_function = delta_function
        self.delta_change_id = 0
        self.device_values = {}

    def update(self, device_urns):
        """Get the latest delta from the client and update our stored values."""
        # Remove devices that are no longer present.
        self.device_values = {device_urn : value for device_urn, value in self.device_values.items() if device_urn in device_urns}

        # Get new or changed device values.
        self.delta_change_id, delta = check_api_call(self.delta_function(self.delta_change_id))
        for device_urn, value in delta:
            self.device_values[device_urn] = value

    def value(self, device_urn, default=None):
        """Return stored value for specified device, or default value if not found."""
        if device_urn in self.device_values:
            return self.device_values[device_urn]
        return default


def device_display_name(device_services, device_urn):
    """Get the display name for a device."""
    user_id_result, user_id = device_services.user_id(device_urn)
    if not user_id_result:
        user_id = 0
    user_name_result, user_name = device_services.name(device_urn)
    if not user_name_result:
        user_name = ""
    display_type_result, display_type = device_services.display_type(device_urn)
    if not display_type_result:
        # Fallback to device type, which is still available for missing devices.
        device_type = check_api_call(device_services.device_type(device_urn))
        display_type = device_type
    if user_name:
        return "{} {} ({})".format(user_id, user_name, display_type)
    return "{} ({})".format(user_id, display_type)


def _platform_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Use msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys
    import tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    return _getch
_GET_CHAR_FUNC = _platform_getch()


def check_api_call(api_return):
    """Check the result on an API call and raise an exception on failure. Return any other values to the caller."""
    if isinstance(api_return, Result) or isinstance(api_return, bool):
        if api_return:
            return None
        raise RPCError(api_return)
    if not api_return[0]:
        raise RPCError(api_return[0])
    if len(api_return) > 2:
        return api_return[1:]
    return api_return[1]


def print_api_call(api_return):
    """Check the result on an API call and print the result to the console. Return any other values to the caller."""
    if isinstance(api_return, Result) or isinstance(api_return, bool):
        print(api_return)
        return None
    print(api_return[0])
    if len(api_return) > 2:
        return api_return[1:]
    return api_return[1]


def check_connected(client, vicon_core_api=None):
    """Check the client is connected to an instance of the application. Raise an error if it isn't."""
    from vicon_core_api import Client, Result, RPCError

    if not client.connected:
        raise RuntimeError("Failed to connect to application at {}:{}".format(client.server_endpoint[0], client.server_endpoint[1]))
    else:
        print("Shogun Connected")

def get_standard_key():
    """Returns a single character input via keypress. Input is converted to lower-case, and non-printing characters are ignored."""
    while True:
        key_char = _GET_CHAR_FUNC()
        if key_char in [b'\000', b'\xe0']:
            key_char = _GET_CHAR_FUNC()
        else:
            break
    return key_char.lower()
