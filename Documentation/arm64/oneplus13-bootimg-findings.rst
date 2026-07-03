OnePlus 13 boot.img and dtbo-derived hardware findings
=======================================================

Source analyzed
---------------

The referenced boot image lives in ``skb8/sm8750`` on branch
``feat/sm8750-acpi-madt-gtdt``:

* ``boot.img`` commit: ``c92aeb790bc4cfd5d8a6867553c4f06fc5680eaf``
* blob SHA: ``58e10eccade5eed50f7ae5c614ed77d041b752c4``
* size: ``100663296`` bytes

The same repository contains ACPI extraction notes generated from the matching
``dtbo.img`` and platform work.  Those notes are the useful kernel-facing part:
register ranges, IRQs, GPIOs, panel names, charger/gauge hints, Wi-Fi PCIe
resources and touchscreen wiring.

Kernel changes implied by these findings
----------------------------------------

USB / Type-C
~~~~~~~~~~~~

The boot/dtbo-derived USB topology is:

* DWC3 wrapper/core: ``0x0a600000`` size ``0x100000``
* TCSR dynamic enable/disable: ``0x01fc6000`` size ``0x4``
* DWC3 IRQ: GIC SPI ``133``
* wrapper power-event IRQ: GIC SPI ``130``
* eUSB2 HS PHY: ``0x088e3000`` size ``0x29c``
* eUSB2 refclk block: ``0x088e2000`` size ``0x4``
* USB3/DP QMP combo PHY: ``0x088e8000`` size ``0x3000``
* role: ``otg``
* maximum-speed: ``super-speed-plus``

The branch enables DWC3 gadget, NCM, PMIC GLINK and UCSI.  This should cover
basic USB networking and Type-C/PD discovery once the SM8750 USB nodes probe.

Display
~~~~~~~

The display resources from the extracted notes are:

* splash framebuffer: ``0xfc800000`` size ``0x02b00000``
* resolution: ``1440x3168``
* format: ``a8r8g8b8``
* panel reset GPIO: TLMM ``98``
* backlight enable GPIO: TLMM ``100``
* max brightness: ``4095``
* DSI0 controller: ``0x0ae94000`` size ``0x1000``
* DSI0 PHY: ``0x0ae95000`` size ``0x0a00``
* DSI1 controller: ``0x0ae96000`` size ``0x1000``
* DSI1 PHY: ``0x0ae97000`` size ``0x0a00``
* panel candidates: ``AA545_P_3_A0005``, ``BF262_P_3_A0021``,
  ``AA569_P_3_A0019``
* actual rooted device cmdline reports: ``AA569_P_3_A0019_dsc_cmd``

The live DTS already exposes the simple framebuffer.  Full DRM panel support
still needs a panel node/driver payload for AA569 with DSC timings.

Touchscreen
~~~~~~~~~~~

Confirmed active touchscreen data:

* node: ``synaptics_tcm_hbp@0``
* compatible: ``synaptics,tcm-spi-hbp``
* chip: ``S3910``
* firmware: ``AA545``
* SPI bus: ``qupv3_se4_spi`` / ``a90000.spi`` / ``&spi4``
* CS: ``0``
* max frequency: ``19000000``
* IRQ GPIO: TLMM ``162`` flags ``0x2008``
* reset GPIO: TLMM ``161`` active-low
* AVDD enable GPIO: ``pm8550vs_j_gpios`` GPIO ``3``
* VDD: ``L4B`` / ``vreg_l4b_1p8``
* HBP panel coords: ``23040x50688``
* display coords: ``1440x3168``
* TX/RX: ``17x38`` with ``S3910_PANEL7`` override ``18x40``

The live DTS now includes this node.  Kernel-side support still requires the
community/vendor ``synaptics_tcm_hbp`` / ``synaptics_tcm2`` driver to be built
in-tree or as a module.

Wi-Fi / Bluetooth
~~~~~~~~~~~~~~~~~

The extracted ACPI notes identify WCN7850 resources:

* Wi-Fi chip family: WCN7850
* PCIe root complex: PCIe0 at ``0x01c00000``
* PARF: ``0x01c00000`` size ``0x3000``
* PHY: ``0x01c06000`` size ``0x2000``
* DWC core: ``0x40000000``
* ECAM: ``0x40100000`` size ``0x100000``
* IO window: ``0x40200000`` size ``0x100000``
* MEM32 window: ``0x40300000`` size ``0x03d00000``
* PCIe global IRQ: GIC SPI ``140``
* INTx: GIC SPI ``149`` to ``152``
* PERST GPIO: TLMM ``102`` active-low
* WAKE GPIO: TLMM ``104``
* WLAN enable GPIO: TLMM ``16``

The config fragment enables Qualcomm PCIe, QMP PCIe PHY, ath12k PCI and QCA
Bluetooth UART plumbing.  Device-tree PCIe/WLAN enablement still needs labels
from the SM8750 DTSI to avoid guessing wrong node names.

Battery / charger
~~~~~~~~~~~~~~~~~

The boot/dtbo-derived charging data identifies:

* Oplus mms wired charger framework
* PM8550 virtual buck
* USB temperature ADC channels ``0x74a`` and ``0x75e``
* PM8550 GPIO6 discharge control
* charger UART GPIOs: TLMM ``62`` and ``63``
* nominal capacity: ``5610 mAh``
* silicon-p-770 override: ``5920 mAh``
* wireless charging node present

The branch keeps PMIC GLINK battery/USB/PD as the safe first target.  VOOC,
UFCS, ADSP gauge and Oplus charger features need vendor framework support or a
clean replacement driver.

Thermal / BCL
~~~~~~~~~~~~~

Confirmed thermal/BCL resources:

* PM8010M temp alarm: SPMI SID ``0x0c``, base ``0x2400``
* PM8010N temp alarm: SPMI SID ``0x0d``, base ``0x2400``
* PM8550 temp alarm: SPMI SID ``0x01``, base ``0x0a00``, ADC channel ``0x103``
* PM8550 BCL: base ``0x4700``, size ``0x100``
* BCL interrupt names: ``bcl-lvl0``, ``bcl-lvl1``, ``bcl-lvl2``
* shell thermals are visible on the rooted device: front, frame, back

The config fragment enables Qualcomm SPMI ADC/TM and TSENS.  Safe DTS work left:
port shell thermals and PM8550 GPIO2 thermistor into the live device tree.

Backlight / cover / hall
~~~~~~~~~~~~~~~~~~~~~~~~

Confirmed resources:

* panel backlight enable GPIO: TLMM ``100``
* panel reset GPIO: TLMM ``98``
* magnetic/hall bus: ``i2c@9a4000``
* hall device: ``magnachip@10``, IRQ GPIO ``97`` flags ``0x2008``
* magnetic cover: ``magneticcover@11``, DT reg currently ``0x0f``, IRQ GPIO
  ``65`` flags ``0x2002``

These should be treated as next DTS targets after display/touch boot is stable.
