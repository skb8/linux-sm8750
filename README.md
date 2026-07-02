# OnePlus 13 (dodge) SM8750 Linux bringup

Main branch for this repo work: `oneplus-13-sm8750-bringup-v2`.

Цель ветки: максимально расширить совместимость Linux kernel с OnePlus 13 на Snapdragon 8 Elite / SM8750, не ломая boot мусорным downstream-копипастом. Всё, что безопасно для mainline-style ядра, включается в DTS/config. Всё, что завязано на vendor-only Oplus драйверы, размечается как hardware map и портируется отдельными шагами.

## Легенда поддержки

| Значок | Значение |
| --- | --- |
| ✅ | должно работать или уже включено в live DTS/config |
| 🟨 | частично работает / нужен тест на устройстве |
| 🧪 | железо подтверждено, но нужен порт драйвера или аккуратная mainline-адаптация |
| ❌ | пока не работает в mainline-ядре |

## Источники

| Источник | Что взято |
| --- | --- |
| `sm8750-mainline/linux`, `OnePlus-13-WIP` @ `1f2047e8663eda76c8b172fd3e040e3b3fa17950` | стартовый OnePlus 13 DTS, memory map, simple-framebuffer, ранний bringup, USB/NCM |
| `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`, `oneplus/sm8750_b_16.0.0_oneplus_13` @ `0de73fc272a09a1e12e4e758a4d17ae7108df7fc` | downstream hardware map: touch, charger, NFC, sensors, IR, display overlays, project IDs |
| `skb8/sm8750`, `feat/sm8750-acpi-madt-gtdt`, `dtbo.img` @ `572295afe95ae2350d4a2b9872fed5d1d91a3195` | универсальный DTBO источник для сверки OnePlus 13 overlays, blob SHA `240c20b2649d3daafa4abb7109fd316cd28febd2` |
| Root dump from actual device | confirmed OP5D0DL1/PJZ110, project `23821`, `dtbo_idx=5`, `dtb_idx=2`, panel/touch/audio/power-supply nodes |

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
| CPU | ✅ | SM8750 DTSI описывает 8 Oryon CPU, включены `CONFIG_NR_CPUS=8` и `CONFIG_SCHED_CLUSTER` | Android грузится с performance governor, mainline cpufreq/idle всё ещё нужно валидировать |
| RAM | ✅ | В DTS перенесён OnePlus 13 memory layout из sm8750-mainline dodge | Dump показывает managed memory около 11.3 GiB из-за carveouts, это нормально для Android vendor tree |
| UFS storage | ✅ | Включены `CONFIG_SCSI_UFS_QCOM`, `CONFIG_SCSI_UFS_BSG`, `CONFIG_SCSI_UFS_CRYPTO`, inline encryption | Boot device подтверждён: `soc/1d84000.ufshc` |
| Filesystem encryption | ✅ | `CONFIG_FS_ENCRYPTION`, inline crypto, dm-crypt, F2FS/Btrfs | Подходит для pmOS userdata/rootfs экспериментов |
| Display early boot | ✅ | `simple-framebuffer` 1440x3168, base `0xfc800000`, size `0x2b00000`, `a8r8g8b8` | Dump подтвердил splash region at `0xfc800000` |
| Display panel | 🧪 | Panel name confirmed: `AA569_P_3_A0019_dsc_cmd` | Нужен clean panel node/driver data из downstream display overlay, simplefb уже ок |
| Display DRM/MSM | 🟨 | Включены SM8750 display/GPU clocks и `CONFIG_DRM_MSM` | Hardware exposes DSI0/DSI1 controllers and PHYs, panel still pending |
| GPU | 🟨 | Включён `CONFIG_SM_GPUCC_8750`, DRM/MSM path подготовлен | Android exposes KGSL at `3d00000.qcom,kgsl-3d0`; mainline needs Adreno path/firmware |
| USB gadget | ✅ | Включён `CONFIG_USB_G_NCM` для раннего SSH по USB | Android bootconfig confirms controller `a600000.dwc3` |
| USB Type-C | ✅ | PMIC GLINK/UCSI включены, power_supply показывает `C`, `PD`, `PD_PPS` | Orientation GPIO, похоже, не обязателен для базового UCSI path |
| Buttons | ✅ | Volume Down через PM8550 GPIO6, `gpio-keys`; PMIC PON handles pwrkey/resin | Dump confirms `gpio-keys`, `pmic_pwrkey`, `pmic_resin` inputs |
| Haptics | 🧪 | Dump confirms `qcom-hv-haptics` under PMIH010X | Нужно добавить mainline-compatible haptics node after binding check |
| Touchscreen | 🧪 | Confirmed live Android input: `synaptics-s3910`, `synaptics_tcm_hbp.0`, SPI `a90000.spi`, IRQ GPIO162, reset GPIO161 | Mainline tree lacks Synaptics TCM HBP driver, so live DTS should stay conservative |
| Fingerprint | 🧪 | `oplus_fp_input` exists and touch cmdline has underscreen fingerprint linkage | Needs separate fingerprint userspace/driver and touch coordination |
| Battery / gauge | 🧪 | Battery power_supply works on Android, full/design `5920000`, logs mention `bq28z610` and `silicon_p_770` | Mainline can expose generic PMIC GLINK battery first; VOOC/Oplus gauge is vendor stack |
| Wired charging | 🧪 | PMIC GLINK battery_charger, USB power_supply and Oplus ADSP charger logs confirmed | PD/PPS basic path likely easiest; VOOC/UFCS needs Oplus framework or replacement |
| Wireless charging / OTG boost | 🧪 | Wireless power_supply exists, currently not present | Downstream WLS nodes are vendor-specific, map only for now |
| Thermals | ✅ | Thermal zones confirmed: CPU, GPU, modem, camera, video, DDR, PMIC, shell, USB, battery | Shell thermal and PM8550 GPIO2 are now high-confidence port targets |
| Flash / torch | 🧪 | Downstream sets PM8550 flash/torch current limits; PMIC topology confirmed | Need LED node names from current kernel tree before enabling live |
| NFC | 🧪 | Android platform exposes `soc:nfc_chipset` and `soc:st54spi_gpio` | Better target is likely ST54/ST NFC over SPI/GPIO, not generic PN544 assumption |
| Sensors | 🧪 | Confirmed tof8801 at I2C `5-0041`, hall tri-state, magnetic cover, SSC feedback | Vendor Oplus sensor stack private, but bus addresses are now known |
| IR blaster | 🧪 | Downstream IR remains QUPv3 SE5 SPI, dump exposes SPI controllers `spi0.0` and `spi1.0` | Need identify which `spi1.0` device maps to IR before live enable |
| Cameras | ❌ | Camera/CVP/CDSP carveouts and thermal zones exist | Mainline camera remains blocked by downstream Qualcomm/Oplus camera stack |
| Audio | 🧪 | Dump confirms `sun-mtp-snd-card`, WCD939x codec, RX/TX/VA/WSA macros, SoundWire aliases | Mainline tree does not appear to carry WCD939x codec support yet |
| WLAN | 🟨 | Firmware dirs expose modem images, configs include ath12k | Need board/calibration files and PCIe mapping for WLAN path |
| Bluetooth | 🟨 | Logs show `oplus_btuart_ux`, configs include QCA UART BT | Need exact UART path and firmware file names for clean node |
| Modem / IPA | 🟨 | Android exposes `4080000.remoteproc-mss`, IPA at `3e00000.qcom,ipa`, rmnet-ipa | Userspace firmware/rmtfs/qmi still required |
| Remoteproc / DSP | 🟨 | ADSP `3000000`, CDSP `32300000`, MSS `4080000`, SOCCP and SPSS visible | Useful for audio, sensors, camera, modem, fastrpc |
| LEDs | 🟨 | LED configs enabled, PMIC topology confirmed | Need live PMIC LED node verification before enabling |
| postmarketOS basics | ✅ | dm-crypt, Btrfs, F2FS, zram, WireGuard, binderfs, PSI, UTF-8, NCM | Practical base for rootfs, containers and debugging |

## Что уже добавлено в live DTS/config

- OnePlus 13 DTS skeleton with SM8750 + PMIC includes.
- OnePlus 13 memory map from dodge bringup tree.
- Simple framebuffer for early display.
- PMIC GLINK node for Type-C/charger plumbing.
- Fixed clocks used by the SM8750 tree.
- `vph_pwr` fixed regulator.
- Volume Down key on PM8550 GPIO6.
- Debug UART alias/status.
- Config fragment for UFS, USB NCM, PMIC GLINK, DRM/MSM, LEDs, input, encryption, pmOS basics, WLAN/BT/NFC/SPI/RC experiments.

## Почему не включены все downstream-ноды сразу

OnePlusOSS DTS содержит много `oplus,*` compatible strings. Если просто вставить их в live DTS, mainline kernel их не забиндит, а часть может мешать boot/probe. Правильный путь: live DTS держать boot-safe, а downstream использовать как карту железа.

## OnePlus 13 downstream IDs

Root dump подтвердил, что конкретное устройство использует project ID `23821`, product/model `OP5D0DL1` / `PJZ110`, `dtbo_idx=5`, `dtb_idx=2`. Downstream overlay для него: `dodge-23821-sun-overlay.dts`.

Связанные OnePlus 13 family overlays также есть для `23893`, `23894`, `23895`, но для этого устройства приоритет `23821`.

## DTBO extraction

`dtbo.img` общий для нескольких SM8750-устройств, поэтому фильтровать надо именно dodge / OnePlus 13 IDs.

```sh
git clone https://github.com/skb8/sm8750.git
cd sm8750
git checkout feat/sm8750-acpi-madt-gtdt
mkdir -p out/dtbo
mkdtimg dump dtbo.img -b out/dtbo/dtbo
for dtb in out/dtbo/*.dtb; do
    dtc -I dtb -O dts -o "${dtb%.dtb}.dts" "$dtb"
done
grep -RniE 'dodge|23821|23893|23894|23895|oneplus|OP5D0DL1|PJZ110|AA569|synaptics-s3910' out/dtbo
```

## Следующие порты по приоритету

1. ✅ Проверить boot с appended DTB и simplefb.
2. ✅ Проверить UFS/rootfs, USB NCM и PMIC GLINK Type-C.
3. 🧪 Портировать touchscreen S3910 минимально: SPI, GPIO162 IRQ, GPIO161 reset, питание.
4. 🧪 Добавить shell thermals, PM8550 GPIO2 thermal, haptics and safe LED/flash nodes.
5. 🧪 Разобрать NFC через `soc:nfc_chipset` / `soc:st54spi_gpio`.
6. 🧪 После этого идти в battery/charger, audio, WLAN/BT.
