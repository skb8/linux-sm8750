# OnePlus 13 (dodge) SM8750 Linux bringup

Main branch for this repo work: `oneplus-13-sm8750-bringup-v2`.

Цель ветки: максимально расширить совместимость Linux kernel с OnePlus 13 на Snapdragon 8 Elite / SM8750, включая уже существующие наработки postmarketOS/DTBO/OnePlusOSS. Это не попытка держаться только upstream/mainline-стиля: если железо уже описано и есть рабочий vendor или community path, он фиксируется и подключается.

## GitHub Actions build

Ветка содержит workflow `.github/workflows/oneplus13-kernel.yml`. Он собирает:

- `arch/arm64/boot/Image.gz`
- `arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dtb`
- итоговый `.config`

Артефакт называется `oneplus13-sm8750-kernel`.

## Легенда поддержки

| Значок | Значение |
| --- | --- |
| ✅ | должно работать или уже включено в live DTS/config |
| 🟨 | частично работает / нужен тест на устройстве |
| 🧪 | железо подтверждено, но нужен порт драйвера или сборка внешнего модуля |
| ❌ | пока не работает |

## Источники

| Источник | Что взято |
| --- | --- |
| `sm8750-mainline/linux`, `OnePlus-13-WIP` @ `1f2047e8663eda76c8b172fd3e040e3b3fa17950` | стартовый OnePlus 13 DTS, memory map, simple-framebuffer, ранний bringup, USB/NCM |
| `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`, `oneplus/sm8750_b_16.0.0_oneplus_13` @ `0de73fc272a09a1e12e4e758a4d17ae7108df7fc` | downstream hardware map: touch, charger, NFC, sensors, IR, display overlays, project IDs |
| `skb8/sm8750`, `feat/sm8750-acpi-madt-gtdt`, `dtbo.img` @ `572295afe95ae2350d4a2b9872fed5d1d91a3195` | универсальный DTBO источник для сверки OnePlus 13 overlays, blob SHA `240c20b2649d3daafa4abb7109fd316cd28febd2` |
| Root dump from actual device | confirmed OP5D0DL1/PJZ110, project `23821`, `dtbo_idx=5`, `dtb_idx=2`, panel/touch/audio/power-supply nodes |
| Community working DTS | Synaptics TCM HBP touchscreen node using `&spi4`, `synaptics,tcm-spi-hbp` |

## Что ещё нужно для доделки функций

| Функция | Чего не хватает | Что именно нужно получить с устройства |
| --- | --- | --- |
| Touchscreen S3910 | Драйвер `synaptics_tcm_hbp` / `synaptics_tcm2` в этом kernel tree | Если после сборки тач не работает: полный `dmesg | grep -Ei 'synaptics|tcm|spi|touch'` и список `/sys/devices/platform/soc/ac0000.qcom,qupv3_1_geni_se/a90000.spi/spi_master/spi0/spi0.0/` |
| Display DRM panel | Panel init sequence / DSC / timings для `AA569_P_3_A0019_dsc_cmd` | Decompile DTBO index 5 или дамп `/proc/device-tree/soc/qcom,dsi-display-primary` и `/proc/device-tree/soc/*dsi*`; плюс `dmesg | grep -Ei 'dsi|panel|mdss|drm|display'` |
| GPU | Firmware names + Adreno compatibility / GMU bits | `dmesg | grep -Ei 'kgsl|adreno|gmu|gpu|firmware'` и список firmware из `/vendor/firmware*` где есть `a7xx`, `gen70500`, `gmu` |
| Battery/gauge | Mainline path для `bq28z610`/Oplus ADSP gauge | `ls -la /sys/class/power_supply`, `cat /sys/class/power_supply/battery/uevent`, `dmesg | grep -Ei 'bq28|gauge|battery|oplus_chg'` |
| Fast charging / VOOC / UFCS | Oplus charging framework или replacement driver | Логи подключения зарядки: `dmesg -w` при вставке USB-C PD/PPS/VOOC, плюс содержимое `/sys/class/power_supply/usb/uevent` |
| Wireless charging | WLS RX/CP chip details | `dmesg | grep -Ei 'wls|wireless|rx|nu1669|charge'` и `/sys/class/power_supply/wireless/uevent` на беспроводной зарядке |
| NFC | Точный чип/шина/IRQ/reset для `soc:nfc_chipset` / `soc:st54spi_gpio` | `find /proc/device-tree -iname '*nfc*' -o -iname '*st54*' -o -iname '*ese*'`, `ls -la /sys/bus/spi/devices /sys/bus/i2c/devices`, `dmesg | grep -Ei 'nfc|st54|ese|nxp|pn5|sn100'` |
| IR blaster | Подтвердить SPI device и gpio/regulator | `ls -la /sys/bus/spi/devices/spi1.0`, `dmesg | grep -Ei 'ir|kookong|spi1|consumer'`, DT node для `consumerIr` если есть |
| Audio speakers/mic | Полная LPASS/WCD939x/SoundWire карта | `cat /proc/asound/cards`, `cat /proc/asound/pcm`, `find /proc/device-tree -iname '*wcd*' -o -iname '*lpass*' -o -iname '*swr*' -o -iname '*sound*'` |
| WLAN | PCIe path, board data, firmware names | `dmesg | grep -Ei 'ath12k|wlan|pci|mhi|firmware|board'` после включения Wi-Fi и список `/vendor/firmware*/*ath*` `/vendor/firmware*/*wlan*` |
| Bluetooth | UART path + QCA firmware | `dmesg | grep -Ei 'bluetooth|hci|qca|btuart|tty'`, `ls -la /dev/ttyHS* /dev/ttyMSM*`, firmware names из `/vendor/firmware*` |
| Haptics | Mainline-compatible PMIH010X haptics node | `find /proc/device-tree -iname '*haptic*' -o -iname '*vibrator*'` и `dmesg | grep -Ei 'haptic|vibrator'` |
| Cameras | Очень большой downstream camera stack | Пока только если цель именно камера: нужны camera DT overlays, firmware list, `dmesg | grep -Ei 'camera|cam_|csiphy|cci|sensor'` |
| Modem/mobile data | Userspace + firmware/rmtfs/IPA integration | `dmesg | grep -Ei 'mpss|modem|ipa|rmnet|qmi|rmtfs'`, наличие modem firmware, и логи ModemManager/ofono если будешь тестить |

## Подтверждено с устройства

| Поле | Значение |
| --- | --- |
| Android model | `PJZ110` |
| Device / product | `OP5D0DL1` |
| Downstream model | `Qualcomm Technologies, Inc. Sun MTP,dodge` |
| Downstream compatible | `qcom,sun-mtp`, `qcom,sun`, `qcom,sunp-mtp`, `qcom,sunp`, `qcom,mtp` |
| Project ID | `23821` |
| SKU / region | `sku=23`, `oplus_region=151` |
| DTBO / DTB index | `dtbo_idx=5`, `dtb_idx=2` |
| Boot UFS | `1d84000.ufshc` |
| Panel | `mdss_dsi_panel_AA569_P_3_A0019_dsc_cmd`, `PanelID-0x035E7604` |
| Touch | `synaptics-s3910`, input path `spi0.0`, controller `a90000.spi` |
| Audio card | `sun-mtp-snd-card`, codec path exposes `wcd939x-codec` |
| Type-C / charger | PMIC GLINK UCSI exposes USB-C, PD, PD_PPS power supply |
| Battery | reports `5920000` uAh full/design, Li-ion, Oplus battery |
| Wireless charging | power_supply exists, currently `present=0` |
| Thermal zones | shell front/frame/back, PMIC, GPU, camera, video, DDR, USB, battery zones visible |

## Таблица совместимости

| Подсистема | Статус | Как реализовано / как будет работать | Нюансы |
| --- | --- | --- | --- |
| Boot | ✅ | Добавлен `arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts`, включён `CONFIG_ARM64_APPENDED_DTB` | Root dump подтвердил downstream target `sun-mtp,dodge`, project `23821` |
| CPU | ✅ | SM8750 DTSI описывает 8 Oryon CPU, включены `CONFIG_NR_CPUS=8` и `CONFIG_SCHED_CLUSTER` | Android грузится с performance governor, cpufreq/idle надо тестировать |
| RAM | ✅ | В DTS перенесён OnePlus 13 memory layout из sm8750-mainline dodge | Dump показывает managed memory около 11.3 GiB из-за carveouts |
| UFS storage | ✅ | Включены `CONFIG_SCSI_UFS_QCOM`, `CONFIG_SCSI_UFS_BSG`, `CONFIG_SCSI_UFS_CRYPTO`, inline encryption | Boot device подтверждён: `soc/1d84000.ufshc` |
| Display early boot | ✅ | `simple-framebuffer` 1440x3168, base `0xfc800000`, size `0x2b00000`, `a8r8g8b8` | Dump подтвердил splash region at `0xfc800000` |
| Display panel | 🧪 | Panel name confirmed: `AA569_P_3_A0019_dsc_cmd` | Нужен panel node/driver data из downstream display overlay |
| USB gadget | ✅ | Включён `CONFIG_USB_G_NCM` для раннего SSH по USB | Android bootconfig confirms controller `a600000.dwc3` |
| USB Type-C | ✅ | PMIC GLINK/UCSI включены, power_supply показывает `C`, `PD`, `PD_PPS` | Orientation GPIO, похоже, не обязателен для базового UCSI path |
| Buttons | ✅ | Volume Down через PM8550 GPIO6, `gpio-keys`; PMIC PON handles pwrkey/resin | Dump confirms `gpio-keys`, `pmic_pwrkey`, `pmic_resin` inputs |
| Touchscreen | ✅ | В DTS добавлен рабочий `synaptics_tcm_hbp@0` на `&spi4` / `a90000.spi`, IRQ GPIO162, reset GPIO161, AVDD PM8550VS_J GPIO3, VDD `vreg_l4b_1p8`, firmware `AA545` | Нужен сам драйвер `synaptics_tcm_hbp` / `synaptics_tcm2` при сборке, как в pmos/vendor kernels |
| Fingerprint | 🧪 | Touch node оставляет `fingerprint_not_report_in_suspend`; dump confirms `oplus_fp_input` | Требует touch sysfs + fingerprint userspace |
| Battery / gauge | 🧪 | Battery power_supply works on Android, full/design `5920000`, logs mention `bq28z610` and `silicon_p_770` | Basic PMIC GLINK battery first, VOOC/Oplus gauge needs vendor stack |
| Wired charging | 🧪 | PMIC GLINK battery_charger, USB power_supply and Oplus ADSP charger logs confirmed | PD/PPS basic path likely easiest, VOOC/UFCS needs Oplus framework |
| Wireless charging / OTG boost | 🧪 | Wireless power_supply exists, currently not present | Downstream WLS nodes are vendor-specific |
| Thermals | ✅ | Thermal zones confirmed: CPU, GPU, modem, camera, video, DDR, PMIC, shell, USB, battery | Shell thermal and PM8550 GPIO2 are high-confidence port targets |
| NFC | 🧪 | Android platform exposes `soc:nfc_chipset` and `soc:st54spi_gpio` | Target is likely ST54/ST NFC over SPI/GPIO, not generic PN544 assumption |
| Sensors | 🧪 | Confirmed tof8801 at I2C `5-0041`, hall tri-state, magnetic cover, SSC feedback | Vendor Oplus sensor stack private, bus addresses known |
| IR blaster | 🧪 | Downstream IR remains QUPv3 SE5 SPI, dump exposes SPI controllers `spi0.0` and `spi1.0` | Need identify which `spi1.0` maps to IR before live enable |
| Cameras | ❌ | Camera/CVP/CDSP carveouts and thermal zones exist | Blocked by downstream Qualcomm/Oplus camera stack |
| Audio | 🧪 | Dump confirms `sun-mtp-snd-card`, WCD939x codec, RX/TX/VA/WSA macros, SoundWire aliases | Need WCD939x/LPASS driver support in this kernel tree |
| WLAN / BT | 🟨 | ath12k/QCA configs added, logs show `oplus_btuart_ux` | Need board/calibration files, PCIe/UART mapping, firmware names |
| Modem / IPA | 🟨 | Android exposes `4080000.remoteproc-mss`, IPA at `3e00000.qcom,ipa`, rmnet-ipa | Userspace firmware/rmtfs/qmi still required |
| postmarketOS basics | ✅ | dm-crypt, Btrfs, F2FS, zram, WireGuard, binderfs, PSI, UTF-8, NCM | Practical base for rootfs, containers and debugging |

## OnePlus 13 downstream IDs

Root dump подтвердил, что конкретное устройство использует project ID `23821`, product/model `OP5D0DL1` / `PJZ110`, `dtbo_idx=5`, `dtb_idx=2`. Downstream overlay для него: `dodge-23821-sun-overlay.dts`.

Связанные OnePlus 13 family overlays также есть для `23893`, `23894`, `23895`, но для этого устройства приоритет `23821`.
