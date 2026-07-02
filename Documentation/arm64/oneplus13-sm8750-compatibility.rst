OnePlus 13 (dodge) Linux compatibility map
===========================================

Goal
----

Track what the current mainline-facing kernel branch can expose on OnePlus 13, and what still needs driver or DTS work.  This is intentionally hardware-focused and based on:

* ``sm8750-mainline/linux`` branch ``OnePlus-13-WIP`` at ``1f2047e8663eda76c8b172fd3e040e3b3fa17950``
* ``OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`` branch ``oneplus/sm8750_b_16.0.0_oneplus_13`` at ``0de73fc272a09a1e12e4e758a4d17ae7108df7fc``
* ``skb8/sm8750`` ``dtbo.img`` at ``572295afe95ae2350d4a2b9872fed5d1d91a3195`` with blob SHA ``240c20b2649d3daafa4abb7109fd316cd28febd2``

Compatibility table
-------------------

===================== ===================== ================================================================
Area                  Branch status         Notes / next kernel work
===================== ===================== ================================================================
Boot                  improved              Added dedicated OnePlus 13 DTS, appended-DTB config, PMIC includes.
CPU / scheduler       enabled               8 Oryon CPUs, sched cluster config enabled.
RAM                   improved              16 GiB OnePlus 13 memory layout copied from sm8750-mainline dodge.
UFS storage           enabled               UFS QCOM, BSG, inline crypto, fscrypt enabled in config fragment.
Display boot          improved              Simple-framebuffer 1440x3168 at ``0xfc800000`` from dodge sources.
Display DRM/MSM       config-enabled         SM8750 DPU/DSI path enabled, panel still needs a clean upstream node.
USB gadget            improved              NCM gadget enabled for SSH, serial gadget intentionally disabled.
USB Type-C            partial               PMIC GLINK/UCSI enabled, role/orientation GPIO still unresolved.
Buttons               improved              Volume Down key added on PM8550 GPIO6.
Touchscreen           mapped                Synaptics S3910 over QUPv3 SE4 SPI, IRQ GPIO162, reset GPIO161.
Touch userspace       blocked               Downstream uses Oplus/Synaptics HBP stack, not mainline-ready yet.
Battery / charging    mapped                5610 mAh, dual battery, PM8550 charger, VOOC/UFCS in downstream.
Battery mainline      partial               Generic PMIC GLINK path enabled, Oplus charger framework not ported.
Thermals              mapped                PM8550 GPIO2 thermistor and shell temp nodes identified downstream.
Flash / torch         mapped                PM8550 flash/torch channels use 5000 uA current limit downstream.
NFC                   mapped                Downstream has dodge NFC overlay, needs compatible-string cleanup.
Sensors               mapped                SSC feedback, IR blaster over QUPv3 SE5 SPI, hall/magnetic cover found.
IR blaster            mapped                ``oplus,kookong_ir_spi`` on SE5 SPI, MOSI GPIO53, 5 MHz.
Cameras               reserved              Camera/CVP/CDSP memory carved out, camera stack remains downstream-only.
Audio                 config-gap            Qualcomm/LPASS path not enabled here yet, needs codec/AFE mapping.
WLAN / BT             config-ready           Debug configs enabled, firmware/calibration integration still external.
Fingerprint           mapped                Downstream touch stack flags underscreen fingerprint dependencies.
Modem / IPA           memory-ready           MPSS/IPA memory regions are present in SoC tree, userspace still needed.
PostmarketOS basics   improved              dm-crypt, Btrfs, F2FS, zram, WireGuard, binderfs, PSI enabled.
===================== ===================== ================================================================

Downstream hardware IDs
-----------------------

The OnePlusOSS dodge overlay lists project IDs ``23893``, ``23894`` and ``23895`` for the OnePlus 13 family.  It targets hardware IDs ``T1``, ``EVT1``, ``EVT2``, ``DVT1``, ``DVT2`` and ``PVT1``.

Do not blindly import downstream-only nodes into the live DTS.  Many use private Oplus compatibles and will not bind on a mainline kernel.  The branch keeps those as a map so they can be ported one subsystem at a time without poisoning boot.
