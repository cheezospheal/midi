# MIDI
A custom PCB designed to play melodies on a keypad, switch to different octaves, and includes a screen that shows what note you're playing!

While I've never been too interested in music (I'm very musically illiterate and got absolutely terrible marks in all of my music classes), I AM interested in hardware. I tried to make my MIDI very not-music-focused, or at least, very simple so even people like me can understand. A MIDI is essentially an instrument that that does not literally emit sound, but rather transmits to the computer what to play. It's also a little more complex than just a PCB with an OLED, so I get to use some more of my PCB designing skills and practice making something completely new! It being interactive as well opens up a lot more possibilities for what I can do with the PCB, and I tried to make it as custom as I can with my current skill level. 

<img width="450" height="450" alt="Untitled design (2)" src="https://github.com/user-attachments/assets/47bd4a57-4d55-4e1e-b6fe-65d4b3c9fda9" />

## Features
* 7 capacitive touch keys that correspond to the 7 notes of a C Major Scale
* 5 RGB LED lights that cycle through an animation
* A mod wheel in a potentiometer slider for adding filters/expression
* A volume change potentiometer slider
* 2 key switches that allow for changing the octave [Custom]
* 1 key switch that plays a kick drum
* An OLED that will display what note is being played [Custom]
  
## Summary
The PCB and schematic were designed in **KiCad** and the firmware was coded in **VS Code** (in advance) using **KMK** and **CircuitPython**. Please see the files below to import what you need into the respective softwares.

### General Files
|File|What's Inside?|
|---|---|
|midi.kicad_pcb|contains the PCB layout, including the footprints, footprints, and edge cuts|
|midi.kicad_pro|contains the project settings and configuration|
|midi.kicad_sch|contains the schematic and connections|
|midi_gerbers.zip|contains several gerber files|
|code.py|contains the firmware used to run the microcontroller|

### External Libraries
There are several libraries that are also needed to run the firmware! Please download the following files from the following links:
|File/Folder|What does it do?|Link|
|---|---|---|
|adafruit_displayio_ssd1306.mpy|contains info for CircuitPython on how to initialize the OLED and draw pixels|https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases (Extract from the lib folder in the bundle)|
|adafruit_display_text|allows the OLED to display texts and fonts|https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases (Extract from the lib folder in the bundle)|
|adafruit_midi|contains standard MIDI info, functions, and data|https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases (Extract from the lib folder in the bundle)|
|kmk|firmware for use with CircuitPython specifically for custom keyboards and MIDIs|https://github.com/KMKfw/kmk_firmware|

## Schematic
The schematic is located inside the midi.kicad_sch file, and you'll notice some parts of interest. 
* [U1] Waveshare ESP32-S3-ZERO (microcontroller)
* [SW_1, SW_2, SW_3] SW_Push (tactile push switches)
* [RV1, RV2] R_Potentiometer_MountingPin (slider potentiometers)
* [J1] Conn_01x07_Pin (connecting pins for the capacitive touch keys)
* [J2] Conn_o1x04_Pin (connecting pins for the OLED)
* [D1, D2, D3, D4, D5] SK6812MINI-E (RGB LEDs)
* [R1] 330 (330 Ohm Resistor)

<img width="654" height="413" alt="image" src="https://github.com/user-attachments/assets/f1ea8faf-e55c-43e6-b182-c86fcf097b98" />

Use the pins as reference for the firmware later on!
|GPIO|Component|Part|
|---|---|---|
|GPIO1|I2C SCL|OLED|
|GPIO2|I2C SDA|OLED|
|GPIO3|SLIDE1|Potentiometer RV1|
|GPIO4|Slide2|Potentiometer RV2|
|GPIO5|LED|RGB LEDs|
|GPIO6|SWITCH3|Tactile Push Switch SW3|
|GPIO7|TOUCH7|Capacitive Touch Keys|
|GPIO8|TOUCH6|Capacitive Touch Keys|
|GPIO9|TOUCH5|Capacitive Touch Keys|
|GPIO10|TOUCH4|Capacitive Touch Keys|
|GPIO11|TOUCH3|Capacitive Touch Keys|
|GPIO12|TOUCH2|Capacitive Touch Keys|
|GPIO13|TOUCH1|Capacitive Touch Keys|
|GPIO43|SWITCH1|Tactile Push Switch SW1|
|GPIO44|SWITCH2|Tactile Push Switch SW2|

## Routing & Customization
Open up the .kicad_pcb file to see the PCB in the editor! The routing was made using both F.cu and B.cu layers, with vias to connect them. I also added a GND pour, so I don't have to route any of the GND ratlines on the back. However, make sure you don't include the GND pour on the capacitive touch keys! The image graphics were added using KiCad's built in image converter, where you can upload any image and it will automatically convert into a black and white bitmap for you to add. Then, just add it in as a footprint (you may need your own .pretty library for this) and edit it to be on the F.Silkscreen layer in the footprint editor. The text is much simpler, just use KiCad's built in text function and write your text! KiCad has multiple fonts to use, so I used Wingdings and Bell MT. If you want to see how your PCB will probably eventually look like, you can open it up in the 3D Viewer! 

<img width="524" height="420" alt="image" src="https://github.com/user-attachments/assets/e5620950-c8f2-46be-a742-f43bef8831ce" />

## Firmware
(For Half Life, I used the MIDI tutorial's firmware as a base)
Open up the code.py file in VS Code if you want to edit it in advance (if you don't have your physical PCB yet) or you can connect the microcontroller via USB to your computer.

#### Setup
```python
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
```
The first part of the code imports the tools we need from specific libraries, which need to be downloaded (see External Libraries). The io libraries are built in, so no need to download those.

#### Touch Scanner
```python
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
```

This part of the code is a touch scanner for the capacitive touch keys, which can detect which key is pressed and whether it is pressed or not. The if statement inside the if touched != self.pressed[i] was added by me, and it is the part that displays what note is being played on the OLED (explained in more detail below). 

#### OLED
```python
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
```  
This is the setup for the different components of the MIDI, such as the keys, volume change, and the OLED. The OLED needs to have the i2c labeled, the address given, and the dimensions configured. In the OLED stuff section, there'll be the actual firmware for how the OLED detects what to display (coded by me!). It uses a label that refers to a set called NOTE_NAMES. When a note isn't playing, it will just display "-", but when it is, it will use the index from the touch keys (for what number key is playing) and refer to the set (C, D, E, F, G, A, B), with indexes from 0 to 6 referring to each note respectively. 

#### Pin Numbers
```python
keyboard.matrix = [
    # Touch pads 1-7 (keys 0-6)
    TouchScanner([pin.GPIO13, pin.GPIO12, pin.GPIO11, pin.GPIO10, pin.GPIO9, pin.GPIO8, pin.GPIO7]),
    # Switches SW1-SW3 (keys 7-9)
    KeysScanner([pin.GPIO6, pin.GPIO43, pin.GPIO44], value_when_pressed=False, pull=True),
]
```
This is where all the GPIO pins are referenced, so if you are updating the pins make sure to update the firmware as well! <br>

#### Octave Change
```python
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
```
This is another custom section that that changes the octave of each key when the first and second switch are pressed, then switches back to the normal octave when they are let go. What is important to note is that the switch doesn't actually make the note change octaves, but rather plays an entirely new note. You probably won't notice this, though, unless you look at the firmware >:) 

The code works in layers, where there is a normal layer, a higher octave layer, and a lower octave layer. The first bunch of lines refers to the notes played at the normal octave, the second bunch refers to the higher octave, and the third bunch refers to the lower octave. There are 7 KC.MIDI_NOTE(#), which refer to each note played when a touch key is pressed. The three lines following those refer to the functions of the switches. The first and second buttons switch to the higher and lower layers respectively, and the third switch plays a kick drum (it also uses KC.MIDI_NOTE). 

#### Sliders, RGB Lights
```python
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
```
This final area of code is for the rest of the functions (sliders, RGB lights), and was left mostly unchanged. The one thing I did change though was the animation playing on the RGB lights (changed to RAINBOW_BREATHE), since I thought it might look cooler.

## Bill of Materials
Please note that this BOM is for general users! For Half Life, please view the BOM submitted on the Half Life website. Also note that these prices are given without any special discounts, but AliExpress often gives discounts anyways, so prices are probably cheaper than shown. Shipping is based off my own address and the tax is calculated with the Ontario rate of 13%. 

|Part|Price (USD)|Quantity Used|Vendor|Link|
|---|---|---|---|---|
|PCB|$12.70|1|JLCPCB|https://jlcpcb.com/|
|Waveshare ESP32-S3-ZERO|$3.56|1|AliExpress|https://www.aliexpress.com/item/1005007948911104.html?src=google&src=google&albch=shopping&acnt=677-394-9260&isdl=y&slnk=&plac=&mtctp=&albbt=Google_7_shopping&aff_platform=google&aff_short_key=_oFgTQeV&gclsrc=aw.ds&albagn=888888&ds_e_adid=&ds_e_matchtype=&ds_e_device=c&ds_e_network=x&ds_e_product_group_id=&ds_e_product_id=en1005007948911104&ds_e_product_merchant_id=5851714237&ds_e_product_country=CA&ds_e_product_language=en&ds_e_product_channel=online&ds_e_product_store_id=&ds_url_v=2&albcp=23838573336&albag=&isSmbAutoCall=false&needSmbHouyi=false&gad_source=1&gad_campaignid=23843844140&gbraid=0AAAABCtupDPue3-xCwmVvJcb3nqWDDgmn&gclid=Cj0KCQjwrvHWBhDKARIsABmp7h1pBcGAcLLLmYV95D3AN_8gVdcy4el_jwCGC9PHR4R6y6rGWIvplrwaAn7eEALw_wcB|
|SK6812 RGB LEDs|$2.61|1|AliExpress|[https://www.aliexpress.com/item/1005007863635868.html?spm=a2g0o.productlist.main.1.467e66echpig2D&algo_pvid=17f43b4a-c6ec-4e01-9861-3f38f1696518&algo_exp_id=17f43b4a-c6ec-4e01-9861-3f38f1696518-0&pdp_ext_f=%7B%22order%22%3A%22641%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21CAD%216.71%211.42%21%21%214.68%210.99%21%402101c69517929046052793291e0d52%2112000042594617264%21sea%21CA%218338085966%21ABX%211%210%21n_tag%3A-29910%3Bd%3Ac42caa26%3Bm03_new_user%3A-29895%3BpisId%3A5000000218625932&curPageLogUid=AQFVQ5jQSkKF&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005007863635868%7C_p_origin_prod%3A](https://www.aliexpress.com/item/1005005193716172.html?spm=a2g0o.cart.0.0.69e838dal0d3wx&mp=1&pdp_npi=6%40dis%21CAD%21CAD+3.65%21CAD+3.65%21%21CAD+3.65%21%21%21%402101ea8f17929799530491274e077e%2112000032072424633%21ct%21CA%218338085966%21%211%210%21)|
|330Ω Resistor|$2.11|1|Sayal Electronics|https://secure.sayal.com/STORE4/prodetails.php?SKU=198449|
|Bourns 15mm Slide Potentiometer|$1.95|2|Digikey|https://www.digikey.ca/en/products/detail/bourns-inc/PTA1543-2010CIB103/3781161|
|Low Choc Kailh Key Switches|$7.99|1|AliExpress|https://www.aliexpress.com/item/1005008883418065.html?spm=a2g0o.productlist.main.1.1c9e5913F8kBSt&algo_pvid=278c7c25-9ab1-4a2a-9760-88be0dc0cf20&algo_exp_id=278c7c25-9ab1-4a2a-9760-88be0dc0cf20-0&pdp_ext_f=%7B%22order%22%3A%221409%22%2C%22spu_best_type%22%3A%22price%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21CAD%2111.19%212.96%21%21%217.81%212.07%21%402101c69517929071229613399e0f00%2112000047082945007%21sea%21CA%218338085966%21ABX%211%210%21n_tag%3A-29910%3Bd%3Ac42caa26%3Bm03_new_user%3A-29895%3BpisId%3A5000000218625932&curPageLogUid=Vd6zfVEWhxYp&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005008883418065%7C_p_origin_prod%3A|
|Low Choc Kailh Key Caps|$4.35|1|AliExpress|[https://www.aliexpress.com/item/1005009278324475.html?spm=a2g0o.productlist.main.7.44362d34xEB8gR&algo_pvid=9f630577-147e-4a07-a9a7-5f5d71948c36&algo_exp_id=9f630577-147e-4a07-a9a7-5f5d71948c36-6&pdp_ext_f=%7B%22order%22%3A%22173%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21CAD%217.65%211.42%21%21%215.34%210.99%21%402101dedf17929083063836626e0f26%2112000048589993989%21sea%21CA%218338085966%21ABX%211%210%21n_tag%3A-29910%3Bd%3Ac42caa26%3Bm03_new_user%3A-29895%3BpisId%3A5000000218625932&curPageLogUid=x2W0Y7VzQsWN&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005009278324475%7C_p_origin_prod%3A](https://www.aliexpress.com/item/1005006734545486.html?spm=a2g0o.cart.0.0.69e838dal0d3wx&mp=1&pdp_npi=6%40dis%21CAD%21CAD+6.09%21CAD+6.09%21%21CAD+6.09%21%21%21%402101ea8f17929799530491274e077e%2112000044697706461%21ct%21CA%218338085966%21%211%210%21&pdp_ext_f=%7B%22cart2PdpParams%22%3A%7B%22pdpBusinessMode%22%3A%22retail%22%7D%7D)|
|96" 128 x 64 OLED|$2.73|1|AliExpress|https://www.aliexpress.com/item/1005006141235306.html?spm=a2g0o.cart.0.0.69e838dal0d3wx&mp=1&pdp_npi=6%40dis%21CAD%21CAD+3.82%21CAD+3.82%21%21CAD+3.82%21%21%21%402101ea8f17929799530491274e077e%2112000035944225407%21ct%21CA%218338085966%21%211%210%21|
|Taxes & Shipping|$20.82|-|-|-|
|Total|$60.77|-|-|-|

## Extra Notes [Half Life]
Note that, for the cart screenshots submitted on the Half Life website, all prices are in CAD. However, all prices have been converted for each individual item into USD for the BOM, thus there may be a small rounding error (will most likely negligible; I can pay the difference out of pocket). Furthermore, there are special discounts (specifically for AliExpress) located in the BOM.csv from Half Life, which is why I am able to afford it under the $30 budget. Additionally, for providing the grant, please look at the BOM submitted on Half Life, not the BOM.csv here (as the BOM on Half Life is under $30).

Please pay attention to the descriptions of each item! Those that are labeled with [OUT OF POCKET] and [ALREADY OWNED] are not purchased with the grant and thus cost $0.01. Additionally, the vendors labeled (Local) are local to me, so I do not have to pay for shipping as I can go to them in person. All shipping prices are based on my own address and ability to go in-person for certain vendors.

I'm really proud of my MIDI and I hope you are too! While I'm no expert in PCBs, I've at least made a lot more progress and was able to add more custom features than I did with my Starbie. Good luck with reviewing! 
