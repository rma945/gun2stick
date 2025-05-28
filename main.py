import argparse
import uinput
import threading
import sys
import evdev

GAMEPAD_DEFAULT_MIN = -32768
GAMEPAD_DEFAULT_MAX = 32767
DEBUG = False

def get_device_names():
    for path in evdev.list_devices():
        device = evdev.InputDevice(path)
        print(f"Device name: {device.name}\n  - phys: {device.phys}\n  - path: {device.path}")


def init_mouses(input_devices: list, input_paths: list, sensetivity: int):
    devices = {}

    def is_relative(capabilities):
        for (etype_name, _), codes in capabilities.items():
            if etype_name == 'EV_REL':
                rel_codes = {code if isinstance(code, str) else code[0] for code in codes}
                return 'REL_X' in rel_codes and 'REL_Y' in rel_codes
        return False

    def is_absolute(capabilities):
        for (etype_name, _), codes in capabilities.items():
            if etype_name == 'EV_ABS':
                abs_names = {code[0][0] for code in codes}
                return 'ABS_X' in abs_names and 'ABS_Y' in abs_names
        return False

    for name in input_devices:
        if DEBUG:
            print(f"Processing device name: {name}")

        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            if name == device.name:
                capabilities = device.capabilities(verbose=True)
                if is_relative(capabilities):
                    devices.update({name: {"path": path, "type": 'rel', "sensetivity": sensetivity }})
                    continue
                elif is_absolute(capabilities):
                    devices.update({name: {"path": path, "type": 'abs', "sensetivity": sensetivity }})
                    continue
                else:
                    print(f"ERROR: Device '{name}' is not recognized as mouse")
                    if DEBUG:
                        print(capabilities)

    for path in input_paths:
        if DEBUG:
            print(f"Processing device path: {path}")

        device = evdev.InputDevice(path)
        capabilities = device.capabilities(verbose=True)
        if is_relative(capabilities):
            devices.update({device.name: {"path": path, "type": 'rel', "sensetivity": sensetivity }})
            continue
        elif is_absolute(capabilities):
            devices.update({device.name: {"path": path, "type": 'abs', "sensetivity": sensetivity }})
            continue
        else:
            print(f"ERROR: Device path '{path}' is recognized as mouse")
            if DEBUG:
                print(capabilities)

    if DEBUG:
        print(f"Found devices: {devices}")

    return devices


def init_gamepads(device_dict):
    gamepads = []

    for i in range(len(device_dict)):
        gamepads.append(uinput.Device(
            name=f"Mouse gamepad {i}",
            events=[
                uinput.ABS_X + (GAMEPAD_DEFAULT_MIN, GAMEPAD_DEFAULT_MAX, 0, 0),
                uinput.ABS_Y + (GAMEPAD_DEFAULT_MIN, GAMEPAD_DEFAULT_MAX, 0, 0),
                uinput.BTN_A,
                uinput.BTN_B,
                uinput.BTN_X
            ]
        ))

    return gamepads


def mouse_events(mouse, gamepad):
    mouseInputEvent = evdev.InputDevice(mouse["path"])
    sensitivity = mouse["sensetivity"]
    mouseType = mouse["type"]
    x = 0
    y = 0

    def mouse_abs_coords(val, min_in, max_in, min_out=GAMEPAD_DEFAULT_MIN, max_out=GAMEPAD_DEFAULT_MAX):
        return int((val - min_in) / (max_in - min_in) * (max_out - min_out) + min_out)

    if mouseType == 'abs':
        abs_x = mouseInputEvent.absinfo(evdev.ecodes.ABS_X)
        abs_y = mouseInputEvent.absinfo(evdev.ecodes.ABS_Y)

        for event in mouseInputEvent.read_loop():
            if event.type == evdev.ecodes.EV_ABS:
                if event.code == evdev.ecodes.ABS_X:
                    x = mouse_abs_coords(event.value, abs_x.min, abs_x.max)
                    gamepad.emit(uinput.ABS_X, x, syn=False)
                elif event.code == evdev.ecodes.ABS_Y:
                    y = mouse_abs_coords(event.value, abs_y.min, abs_y.max)
                    gamepad.emit(uinput.ABS_Y, y, syn=False)

            elif event.type == evdev.ecodes.EV_KEY:
                if event.code == evdev.ecodes.BTN_LEFT:
                    gamepad.emit(uinput.BTN_A, event.value)
                elif event.code == evdev.ecodes.BTN_RIGHT:
                    gamepad.emit(uinput.BTN_B, event.value)
                elif event.code == evdev.ecodes.BTN_MIDDLE:
                    gamepad.emit(uinput.BTN_X, event.value)
            gamepad.syn()

    elif mouseType == 'rel':
        for event in mouseInputEvent.read_loop():
            if event.type == evdev.ecodes.EV_REL:
                if event.code == evdev.ecodes.REL_X:
                    x = max(GAMEPAD_DEFAULT_MIN, min(GAMEPAD_DEFAULT_MAX, x + event.value * sensitivity))
                    gamepad.emit(uinput.ABS_X, x, syn=False)
                elif event.code == evdev.ecodes.REL_Y:
                    y = max(GAMEPAD_DEFAULT_MIN, min(GAMEPAD_DEFAULT_MAX, y + event.value * sensitivity))
                    gamepad.emit(uinput.ABS_Y, y, syn=False)

            elif event.type == evdev.ecodes.EV_KEY:
                if event.code == evdev.ecodes.BTN_LEFT:
                    gamepad.emit(uinput.BTN_A, event.value)
                elif event.code == evdev.ecodes.BTN_RIGHT:
                    gamepad.emit(uinput.BTN_B, event.value)
                elif event.code == evdev.ecodes.BTN_MIDDLE:
                    gamepad.emit(uinput.BTN_X, event.value)
            gamepad.syn()


def run_binding(devices: dict, gamepads: list,):
    threads = []

    for k, v in enumerate(devices):
        print(f"Mapping device: '{v}' to 'Mouse gamepad {k}'")
        t = threading.Thread(
            target=mouse_events,
            args=(devices[v], gamepads[k]),
            daemon=True,
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device-name", action='append', dest="devices", default=[], help="Input device names that will-be mapped into gamepads")
    parser.add_argument("-p", "--device-path", action='append', dest="path", default=[], help="Input device paths that will-be mapped into gamepads")
    parser.add_argument("-s", "--sensetivity", dest="sensetivity", default=100, help="Gamepads sensetivity")
    parser.add_argument("-l", "--list", action=argparse.BooleanOptionalAction, help="Get list of devices")
    parser.add_argument("--debug", action=argparse.BooleanOptionalAction, help="Enable debug")
    args = parser.parse_args()

    if args.list:
        get_device_names()
        sys.exit(0)

    if len(args.devices) == 0 and len(args.path) == 0:
        print("Error: Please define at least one device name or device path")
        sys.exit(0)

    return args


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        DEBUG = True
        print(f"Input args: {args}")

    input_device_names = args.devices
    input_device_paths = args.path

    devices = init_mouses(input_device_names, input_device_paths, args.sensetivity)
    gamepads = init_gamepads(devices)

    run_binding(devices, gamepads)
