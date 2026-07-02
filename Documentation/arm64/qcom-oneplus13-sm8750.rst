OnePlus 13 (SM8750, dodge) bringup notes
=========================================

This branch carries the mainline-facing OnePlus 13 bringup work on top of the current Linux tree.

Source material used:

* sm8750-mainline/linux OnePlus-13-WIP, commit 1f2047e8663eda76c8b172fd3e040e3b3fa17950.
* OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750, branch oneplus/sm8750_b_16.0.0_oneplus_13, commit 0de73fc272a09a1e12e4e758a4d17ae7108df7fc.
* skb8/sm8750 dtbo.img from feat/sm8750-acpi-madt-gtdt.

Current safe bringup target:

* keep the device bootable with appended DTB and simple-framebuffer,
* prefer NCM gadget over serial for early SSH,
* keep Type-C/PMIC-GLINK, UFS inline encryption, SM8750 clocks, pinctrl, interconnect, DRM/MSM, LEDs, and postmarketOS basics enabled,
* avoid importing downstream-only OnePlus drivers as hard dependencies until they have a clean upstream shape.

Known gaps:

* panel, touchscreen, battery/charger, cameras, audio, WLAN firmware integration, and role-switch GPIO still need per-device validation on hardware.
* the postmarketOS wiki is Anubis-protected, so the branch records the upstream repo/commit it references instead of scraping that page.
