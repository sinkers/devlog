---
title: "usbnet: flashing an ESP32 on a Raspberry Pi from a Mac"
subtitle: "macOS has no USB/IP client, so serial boards on a Pi are bridged over RFC2217 instead: what works from a Mac, what doesn't, and why"
tags: [ESP32, Raspberry Pi, macOS, Embedded Systems, Open Source]
canonical: https://sinkers.github.io/devlog/2026/11/28/usbnet/
hero: ../../images/2026-11-28-usbnet/hero.png
hero_alt: "A Mac terminal running usbnet ls, which lists an ESP32 board and a USB missile launcher on a Raspberry Pi, then usbnet esptool chip-id, which connects to the ESP32-S3 over rfc2217:// and starts the flasher stub"
---

If your dev boards live on a bench and your laptop doesn't, you either carry
cables around or put the boards on the network. Linux can do the second with
USB/IP. macOS can't: there is no USB/IP client, and Apple no longer lets
third-party software add a virtual USB host controller.

[usbnet](https://github.com/sinkers/usbnet) gets around that one device
class at a time. A Raspberry Pi with a USB hub publishes each serial board as
an `rfc2217://` port, and esptool on the Mac flashes an ESP32-S3 across the
LAN. On 28 November 2026 it identified the chip, ran the flasher stub and
read back 256 KB of flash byte-identically at 115200 and 460800 baud.

The full write-up covers how it works, the tests, what went wrong (ser2net
couldn't reset an ESP32 into its bootloader over the network; Espressif's own
RFC2217 server can) and the limits from a Mac. Uploads to AVR boards with
avrdude don't work yet, `arduino-cli monitor` won't open a pty, and 921600
baud corrupts reads.
