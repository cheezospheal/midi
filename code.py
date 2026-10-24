import keypad
import touchio
import busio
import terminalio
import displayio
import adafruit_displayio_ssd1306
from adafruit_midi.control_change import ControlChange
from microcontroller import pin

from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.rgb import RGB, AnimationModes
from kmk.keys import KC
from kmk.kmk_keyboard import KMKKeyboard
from kmk.modules.midi import MidiKeys
from kmk.modules.potentiometer import PotentiometerHandler
from kmk.scanners import Scanner
from kmk.scanners.keypad import KeysScanner
from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306

# KMK doesn't have a scanner for touch pads, so here's a tiny one.
# Don't touch the pads while the board boots - they calibrate on startup!
class TouchScanner(Scanner):
    def __init__(self, pins):
        self.pads = [touchio.TouchIn(p) for p in pins]
        self.pressed = [False] * len(pins)

    @property
    def key_count(self):
        return len(self.pads)

    def scan_for_changes(self):
        for i, pad in enumerate(self.pads):
            touched = pad.value
            if touched != self.pressed[i]:
                self.pressed[i] = touched
                if touched:
                    note_label.text = NOTE_NAMES[i]
                else:
                    note_label.text = "-"
                return keypad.Event(i + self.offset, touched)


keyboard = KMKKeyboard()
# These have to be created before we use KC.MIDI_NOTE / KC.VOLU below
midi = MidiKeys()
media_keys = MediaKeys()
displayio.release_displays()
i2c = busio.I2C(scl=pin.GPIO1, sda=pin.GPIO2)
# setup for OLED! 
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# OLED stuff
screen_group = displayio.Group()
display.show(screen_group)
note_label = label.Label(terminalio.FONT, text = "-", scale=3, x=52, y=32)
screen_group.append(note_label)
NOTE_NAMES = ["C", "D", "E", "F", "G", "A", "B"]

keyboard.matrix = [
    # Touch pads 1-7 (keys 0-6)
    TouchScanner([pin.GPIO13, pin.GPIO12, pin.GPIO11, pin.GPIO10, pin.GPIO9, pin.GPIO8, pin.GPIO7]),
    # Switches SW1-SW3 (keys 7-9)
    KeysScanner([pin.GPIO6, pin.GPIO43, pin.GPIO44], value_when_pressed=False, pull=True),
]

# Touch pads play a C major scale, switch 1 changes octave up, switch 2 changes octave down, switch 3 plays a kick drum.
keyboard.keymap = [[
    # Normal octave
    KC.MIDI_NOTE(60), KC.MIDI_NOTE(62), KC.MIDI_NOTE(64), KC.MIDI_NOTE(65),
    KC.MIDI_NOTE(67), KC.MIDI_NOTE(69), KC.MIDI_NOTE(71),
    KC.MO(1),
    KC.MO(2),
    KC.MIDI_NOTE(36),
],
    # Higher octave
[
    KC.MIDI_NOTE(72), KC.MIDI_NOTE(74), KC.MIDI_NOTE(76), KC.MIDI_NOTE(77),
    KC.MIDI_NOTE(79), KC.MIDI_NOTE(81), KC.MIDI_NOTE(83),
    KC.TRNS,
    KC.TRNS,
    KC.TRNS,
],
    # Lower octave
[
    KC.MIDI_NOTE(48), KC.MIDI_NOTE(50), KC.MIDI_NOTE(52), KC.MIDI_NOTE(53),
    KC.MIDI_NOTE(55), KC.MIDI_NOTE(57), KC.MIDI_NOTE(59),
    KC.TRNS,
    KC.TRNS,
    KC.TRNS,

]]


# Sliders send MIDI CC 1 (mod wheel) and CC 7 (volume)
sliders = PotentiometerHandler()
sliders.pins = (
    (pin.GPIO3, lambda state: midi.send(ControlChange(1, state.position))),
    (pin.GPIO4, lambda state: midi.send(ControlChange(7, state.position))),
)

keyboard.modules = [midi, sliders]
keyboard.extensions = [
    media_keys,
    RGB(pixel_pin=pin.GPIO5, num_pixels=5, val_default=80, animation_mode=AnimationModes.BREATHE_RAINBOW),
]

if __name__ == '__main__':
    keyboard.go()