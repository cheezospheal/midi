# Midi
A custom PCB designed to play melodies on a keypad, switch to different octaves, and includes a screen that shows what note you're playing!

While I've never been too interested in music (I'm very musically illiterate and got absolutely terrible marks in all of my music classes), I AM interested in hardware. I tried to make my MIDI very not-music-focused, or at least, very simple so even people like me can understand. A MIDI is essentially an instrument that that does not literally emit sound, but rather transmits to the computer what to play. It's also a little more complex than just a PCB with an OLED, so I get to use some more of my PCB designing skills and practice making something completely new! It being interactive as well opens up a lot more possibilities for what I can do with the PCB, and I tried to make it as custom as I can with my current skill level. 

<img width="481" height="382" alt="image" src="https://github.com/user-attachments/assets/c68aa778-00b9-4652-ad57-0e2e1e5e059e" />

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
|code.py|contains the firmware used to run the micrcontroller|

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

<img width="480" height="314" alt="image" src="https://github.com/user-attachments/assets/4c2b6b31-7559-454f-bbe6-6e0c25eefa26" />

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

<img width="518" height="422" alt="image" src="https://github.com/user-attachments/assets/6baedb85-41f7-437d-9478-a3f271c62096" />

## Firmware
(For Half Life, I used the MIDI tutorial's firmware as a base)
Open up the code.py file in VS Code if you want to edit it in advance (if you don't have your physical PCB yet) or you can connect the microcontroller via USB to your computer.

<img width="347" height="224" alt="image" src="https://github.com/user-attachments/assets/fbc6e0a0-aeb8-4b05-817e-78eaeab16965" />

The first part of the code imports the tools we need from specific libraries, which need to be downloaded (see External Libraries). The io libraries are built in, so no need to download those. 

<img width="349" height="226" alt="image" src="https://github.com/user-attachments/assets/8b527165-0a9e-41f7-b4ab-c88c98724de4" /> <br> <br>
This part of the code is a touch scanner for the capacitive touch keys, which can detect which key is pressed and whether it is pressed or not. The if statement inside the if touched != self.pressed[i] was added by me, and it is the part that displays what note is being played on the OLED (explained in more detail below). <br> <br>

  
<img width="395" height="203" alt="image" src="https://github.com/user-attachments/assets/de349ba9-9286-4609-adb7-2edc9a38e86f" /> <br> <br>
This is the setup for the different components of the MIDI, such as the keys, volume change, and the OLED. The OLED needs to have the i2c labeled, the address given, and the dimensions configured. In the OLED stuff section, there'll be the actual firmware for how the OLED detects what to display (coded by me!). It uses a label that refers to a set called NOTE_NAMES. When a note isn't playing, it will just display "-", but when it is, it will use the index from the touch keys (for what number key is playing) and refer to the set (C, D, E, F, G, A, B), with indexes from 0 to 6 referring to each note respectively. 

<img width="508" height="81" alt="image" src="https://github.com/user-attachments/assets/18ecaa71-3c7c-449b-a0ce-a0ba63b5d8e1" /> <br> <br>
This is where all the GPIO pins are referenced, so if you are updating the pins make sure to update the firmware as well! <br>

<img width="644" height="321" alt="image" src="https://github.com/user-attachments/assets/0f92fd6c-d5a3-4396-9cd5-b5cc38663a9e" /> <br> <br>
This is another custom section that I coded that changes the octave of each key when the first and second switch are pressed, then switches back to the normal octave when they are let go. What is important to note is that the switch doesn't actually make the note change octaves, but rather plays an entirely new note. You probably won't notice this, though, unless you look at the firmware >:) 

The code works in layers, where there is a normal layer, a higher octave layer, and a lower octave layer. The first bunch of lines refers to the notes played at the normal octave, the second bunch refers to the higher octave, and the third bunch refers to the lower octave. There are 7 KC.MIDI_NOTE(#), which refer to each note played when a touch key is pressed. The three lines following those refer to the functions of the switches. The first and second buttons switch to the higher and lower layers respectively, and the third switch plays a kick drum (it also uses KC.MIDI_NOTE). 

<img width="533" height="191" alt="image" src="https://github.com/user-attachments/assets/775f7e29-91fd-4fe9-8e00-00cd7214a4fe" /> <br> <br>
This final area of code is for the rest of the functions (sliders, RGB lights), and was left mostly unchanged. The one thing I did change though was the animation playing on the RGB lights (changed to RAINBOW_BREATHE), since I thought it might look cooler.

## Bill of Materials


