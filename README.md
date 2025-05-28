# 🎯 gun2stick

**gun2stick** is a lightweight Python tool that maps OpenFire lightgun (mouse) devices to virtual gamepads using the Linux `uinput` subsystem.

This allows you to use **two OpenFire lightguns simultaneously** in emulators that only support gamepads or a single mouse input - such as **PCSX2** or **Supermodel3** - enabling true 2-player lightgun gameplay on Linux.

---

## 🚀 Quick Start

### 🔧 Requirements

- Linux with support for `/dev/uinput`
- Python 3.8+
- Required packages:
```bash
pip install evdev python-uinput
```

## 🔒 Permissions

To avoid running as root, create a `udev` rule:

```bash
sudo nano /etc/udev/rules.d/99-uinput.rules
```

Add:

```
KERNEL=="uinput", MODE="0660", GROUP="input"
```

Then:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Make sure your user is part of the `input` group.

---

### 🔌 Setup

1. Connect both OpenFire lightguns to your Linux system.
2. Identify their input device names:
```bash
python3 gun2stick.py --list
```

3. Run the tool with device names:
```bash
python3 gun2stick.py --device "OpenFIRE FIRECon P1 Mouse" --device "OpenFIRE FIRECon P2 Mouse"
```

---

## 🧪 Emulator Configuration Tips

### 🕹 PCSX2

- gun2stick creates a virtual gamepad per lightgun
- In PCSX2, map analog sticks manually in the gamepad settings
- If bindings don’t detect movement:
  - Open `PCSX2.ini` or `Pad.ini` and assign gamepad mappings
```
[USB1]
Type = guncon2
guncon2_Trigger = SDL-0/A
guncon2_ShootOffscreen = SDL-0/B
guncon2_Recalibrate = Keyboard/R
guncon2_RelativeUp = SDL-0/+Axis7
guncon2_RelativeDown = SDL-0/-Axis7
guncon2_RelativeLeft = SDL-0/-Axis6
guncon2_RelativeRight = SDL-0/+Axis6

[USB2]
Type = guncon2
guncon2_Trigger = SDL-1/A
guncon2_ShootOffscreen = SDL-1/B
guncon2_Recalibrate = Keyboard/R
guncon2_RelativeUp = SDL-1/+Axis7
guncon2_RelativeDown = SDL-1/-Axis7
guncon2_RelativeLeft = SDL-1/-Axis6
guncon2_RelativeRight = SDL-1/+Axis6
```

### 🕹 Supermodel3

- Configure the gamepad inputs using your standard configuration method
- Each lightgun should appear as a separate joystick
- Run supermodel with `-print-inputs` argument for get list of inputs
- Edit `Config/Supermodel.ini` file and assign gamepad mappings

```
; player 1
InputGunX = "JOY4_XAXIS"
InputGunY = "JOY4_YAXIS"
InputTrigger = "JOY4_BUTTON1"
InputOffscreen = "JOY4_BUTTON2"
; player 2
InputGunX2 = "JOY5_XAXIS"
InputGunY2 = "JOY5_YAXIS"
InputTrigger2 = "JOY5_BUTTON1"
InputOffscreen2 = "JOY5_BUTTON2"
```

---
