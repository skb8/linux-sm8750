OnePlus 13 boot image derived kernel requirements
=================================================

Source image
------------

The reference boot image is stored in ``skb8/sm8750``:

* branch: ``feat/sm8750-acpi-madt-gtdt``
* commit: ``c92aeb790bc4cfd5d8a6867553c4f06fc5680eaf``
* file: ``boot.img``
* blob SHA: ``58e10eccade5eed50f7ae5c614ed77d041b752c4``
* size: ``100663296`` bytes

The same repository already contains boot/DTBO-derived ACPI notes.  The Linux
bringup-relevant values below are folded back into this kernel tree.

USB / Type-C
------------

Boot-derived hardware map:

* DWC3 core: ``0x0a600000`` size ``0x100000``
* TCSR: ``0x01fc6000`` size ``0x4``
* eUSB2 HS PHY: ``0x088e3000`` size ``0x29c``
* eUSB2 ref clock: ``0x088e2000`` size ``0x4``
* USB3 + DP QMP PHY: ``0x088e8000`` size ``0x3000``
* DWC3 IRQ: GIC SPI ``133``
* wrapper power event IRQ: GIC SPI ``130``
* role: OTG / dual-role
* max speed: super-speed-plus

Kernel requirements already reflected in config:

* ``CONFIG_USB_DWC3``
* ``CONFIG_USB_DWC3_GADGET``
* ``CONFIG_USB_G_NCM``
* ``CONFIG_QCOM_PMIC_GLINK``
* ``CONFIG_UCSI_PMIC_GLINK``
* ``CONFIG_PHY_QCOM_M31_EUSB``
* ``CONFIG_PHY_QCOM_EUSB2_REPEATER``
* ``CONFIG_PHY_QCOM_QMP_COMBO``

Display
-------

Boot/DTBO-derived hardware map:

* MDP core: ``0x0ae00000`` size ``0x93800``
* VBIF: ``0x0aeb0000`` size ``0x2008``
* regdma: ``0x0af80000`` size ``0x7000``
* IPCC: ``0x00400000`` size ``0x2000``
* swfuse: ``0x0af50000`` size ``0x128``
* MDP IRQ: GIC SPI ``83``
* DSI0 controller: ``0x0ae94000`` size ``0x1000``
* DSI0 PHY: ``0x0ae95000`` size ``0xa00``
* DSI1 controller: ``0x0ae96000`` size ``0x1000``
* DSI1 PHY: ``0x0ae97000`` size ``0xa00``
* DP controller ranges: ``0x0af54000`` and QMP DP/USB PHY subranges under ``0x088e8000``
* panel reset GPIO: TLMM ``98`` active-low, post-reset delay ``10 ms``
* backlight enable GPIO: TLMM ``100`` active-high
* panel candidates: ``AA545_P_3_A0005``, ``BF262_P_3_A0021``, ``AA569_P_3_A0019``
* actual rooted device panel: ``AA569_P_3_A0019_dsc_cmd`` / ``PanelID-0x035E7604``
* splash framebuffer: ``0xfc800000`` size ``0x2b00000``

Kernel status:

* simple-framebuffer is wired and should work early.
* DRM/MSM config and SM8750 display clock configs are enabled.
* full panel bringup still needs a panel driver/node with the AA569 DSC command sequence.

Wi-Fi / Bluetooth
-----------------

Boot-derived hardware map:

* combo chip: Qualcomm ``WCN7850``
* Wi-Fi path: PCIe root complex 0, ``pcie0`` at ``0x01c00000``
* PCIe PARF: ``0x01c00000`` size ``0x3000``
* PCIe PHY: ``0x01c06000`` size ``0x2000``
* DWC core: ``0x40000000``
* ECAM: ``0x40100000`` size ``0x100000``
* IO window: ``0x40200000`` size ``0x100000``
* MEM32 window: ``0x40300000`` size ``0x3d00000``
* global IRQ: GIC SPI ``140``
* INTx IRQs: GIC SPI ``149`` to ``152``
* PERST#: TLMM ``102`` active-low
* WAKE#: TLMM ``104`` input
* WLAN enable: TLMM ``16``
* expected PCI IDs: ``17cb:1107`` Wi-Fi and ``17cb:1103`` Bluetooth function

Kernel requirements already reflected in config:

* ``CONFIG_PCI``
* ``CONFIG_PCIE_QCOM``
* ``CONFIG_PHY_QCOM_QMP_PCIE``
* ``CONFIG_ATH12K``
* ``CONFIG_ATH12K_PCI``
* ``CONFIG_BT_QCA``
* ``CONFIG_BT_HCIUART_QCA``

Missing before Wi-Fi can be marked working:

* exact firmware/board files for WCN7850 from Android vendor firmware
* PCIe node confirmation in the SM8750 DTS used by this branch
* runtime dmesg from a boot attempt with this kernel

Battery / charging
------------------

Boot/DTBO-derived hardware map:

* Oplus framework: ``oplus,mms_wired`` + ``oplus,virtual_buck``
* gauge framework: ``oplus,mms_gauge`` + ``oplus,virtual_gauge``
* charger framework version: v2
* capacity: ``5610 mAh`` base, ``5920 mAh`` silicon-p-770 override
* ADC info name: ``855``
* topic update interval: ``5000 ms``
* USB temperature ADC channels: ``0x074a`` and ``0x075e``
* USB temperature conversion ratio: ``10``
* charge UART GPIOs: TLMM ``62`` / ``63``
* discharge GPIO: PM8550 GPIO ``6``
* wireless charging node exists downstream

Kernel status:

* PMIC GLINK battery/charger path is enabled for basic Type-C/PD exposure.
* Oplus VOOC/UFCS/wireless charging stack still needs vendor framework or a replacement driver.

Touchscreen
-----------

Boot/DTBO/root-dump-derived hardware map:

* controller: Synaptics ``S3910``
* node: ``synaptics_tcm_hbp@0``
* compatible: ``synaptics,tcm-spi-hbp``
* firmware: ``AA545``
* bus: QUPv3 SE4 SPI, exposed on Android as ``a90000.spi`` / ``spi0.0``
* max SPI frequency: ``19000000``
* IRQ GPIO: TLMM ``162`` flags ``0x2008``
* reset GPIO: TLMM ``161`` active-low
* AVDD GPIO: ``pm8550vs_j`` GPIO ``3`` active-low
* VDD supply: ``vreg_l4b_1p8``

Kernel status:

* the DTS node is enabled in ``sm8750-oneplus-dodge.dts``.
* config selects ``CONFIG_TOUCHSCREEN_SYNAPTICS_TCM_HBP=m``.
* the actual driver still has to be present in the tree or built as an external module.

Other confirmed boot/root dump clues
------------------------------------

* haptics: PMIH010X ``qcom,hv-haptics@f000``
* proximity sensor: ``tof8801`` at I2C ``5-0041``
* hall sensor: GPIO ``97``
* magnetic cover: GPIO ``65``
* NFC: Android exposes ``soc:nfc_chipset`` and ``soc:st54spi_gpio``
* audio: ``sun-mtp-snd-card``, WCD939x codec, RX/TX/VA/WSA SoundWire macros

These are not all safe to enable blindly, but they are now concrete port targets.
