# Introduction
This repository contains a modified [/IOTCONNECT Python Lite SDK](https://github.com/avnet-iotconnect/iotc-python-lite-sdk) "socket-style" application designed to receive data from any type of application via JSON buffer which it can then transmit to /IOTCONNECT as telemetry. The /IOTCONNECT application can also receive commands from /IOTCONNECT and hand them off to your application(s) through a similar JSON buffer.

This framework allows users to make **minimal modifications** to their existing application(s) while still reaping the full benefits of the /IOTCONNECT platform, and also allows multiple processes to report data to a single /IOTCONNECT cloud connection.

For the the comprehensive guide through setting up any supported device for Plug and Play, see [GUIDE.md](GUIDE.md).

# Verified Development Boards

The following development boards have been tested to support /IOTCONNECT:

* [Microchip Curiosity PIC64GX1000 Kit](microchip-pic64gx1000) - ([Purchase Link](https://www.newark.com/microchip/curiosity-pic64gx1000-kit/curiosity-kit-64bit-risc-v-quad/dp/46AM3917))
* [Microchip PolarFire SoC Discovery Kit](microchip-polarfire-soc-dk) - ([Purchase Link](https://www.avnet.com/americas/product/microchip/mpfs-disco-kit/evolve-67810612/))
* [Microchip ATSAMA5D27-SOM1](microchip-sama5d27) - ([Purchase Link](https://www.avnet.com/shop/us/products/microchip/atsama5d27-som1-ek-3074457345633909354/?srsltid=AfmBOorYtSqVK7BDtS-_h4NDc21QKb7yCg1XAcTrRP8ydEuLJZFjeglj))
* [Microchip SAMA7D65 Curiosity Kit](microchip-sama7d65-curiosity) - ([Purchase Link](https://www.avnet.com/americas/product/microchip/ev63j76a/evolve-118945047/))
* [NXP FRDM-IMX93](nxp-frdm-imx-93) - ([Purchase Link](https://export.farnell.com/nxp/frdm-imx93/frdm-development-board-for-i-mx/dp/4626785))
* [NXP GoldBox 3 Vehicle Networking Development Platform](nxp-s32g-vnp-gldbox3) - ([Purchase Link](https://www.avnet.com/americas/product/nxp/s32g-vnp-gldbox3/evolve-64413515/))
* [Raspberry Pi](raspberry-pi) - ([Purchase Link](https://www.newark.com/raspberry-pi/rpi5-4gb-single/rpi-5-board-2-4ghz-4gb-arm-cortex/dp/81AK1346))
* [ST STM32MP135F-DK Discovery Kit](stm32mp135f-dk) - ([Purchase Link](https://www.newark.com/stmicroelectronics/stm32mp135f-dk/discovery-kit-32bit-arm-cortex/dp/68AK9977))
* [ST STM32MP157F-DK2 Discovery Kit](stm32mp157f-dk2) - ([Purchase Link](https://www.newark.com/stmicroelectronics/stm32mp157f-dk2/discovery-board-32bit-arm-cortex/dp/14AJ2731))
* [ST STM32MP257F-DK Evaluation Board](stm32mp257f-dk) - ([Purchase Link](https://www.avnet.com/americas/product/stmicroelectronics/stm32mp257f-dk/evolve-115914011/))
* [ST STM32MP257F-EV1 Evaluation Board](stm32mp257f-ev1) - ([Purchase Link](https://www.avnet.com/americas/product/stmicroelectronics/stm32mp257f-ev1/evolve-115913010/))
* [Tria MaaXBoard 8M](tria-maaxboard-8m) - ([Purchase Link](https://www.avnet.com/americas/product/avnet-engineering-services/aes-mc-sbc-imx8m-g/evolve-47976882/))
* [Tria MaaXBoard 8ULP](tria-maaxboard-8ulp) - ([Purchase Link](https://www.avnet.com/americas/product/avnet-engineering-services/aes-maaxb-8ulp-sk-g/evolve-57290182/))
* [Tria MaaXBoard OSM93](tria-maaxboard-osm93) - ([Purchase Link](https://www.avnet.com/americas/product/avnet-engineering-services/aes-maaxb-osm93-dk-g/evolve-67866610/))
* [Tria Vision AI-KIT 6490](tria-vision-ai-kit-6490) - ([Purchase Link](https://www.tria-technologies.com/product/vision-ai-kit-6490/))
* [Tria ZUBOARD-1CG](tria-zuboard-1cg) - ([Purchase Link](https://www.avnet.com/americas/product/avnet-engineering-services/aes-zub-1cg-dk-g/evolve-54822506/))

# Getting Started on Your Board with the /IOTCONNECT Python Lite SDK

Since configuring the hardware and software of your device and onboarding it into /IOTCONNECT are the first steps of the Plug and PLay process, 
it is recommended that before jumping into Plug and Play that you first follow your board's specific Quickstart located in the 
[/IOTCONNECT Python Lite Demos](https://github.com/avnet-iotconnect/iotc-python-lite-sdk-demos/tree/main) repository. It will walk you through 
every cable connection, terminal command, and file needed to get your board connected to /IOTCONNECT.

This will set you up in the perfect position to easily swap out the Python Lite Quickstart /IOTCONNECT application with the 
Plug and Play application.

[The Plug and Play guide](GUIDE.md) will refer you to your board's Quickstart for the device setup and onboarding 
process if you do not wish to do those at this time, as it is a mandatory step for all supported boards. After that, the 
only remaining steps are template creation and sending the desired data from your application to a JSON buffer, 
both of which are very simple and also covered in the guide.

# AWS Greengrass Demos Enablement

To explore setting up AWS Greengrass Lite on some of these same devices and deploying python demos through pre-built or custom
components, check out the [/IOTCONNECT Python Greengrass Demos repo](https://github.com/avnet-iotconnect/iotc-python-greengrass-demos/tree/main).

## Licensing

This library is distributed under
the [MIT License](https://github.com/avnet-iotconnect/iotc-c-lib/blob/master/LICENSE.md).

