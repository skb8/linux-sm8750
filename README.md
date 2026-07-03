# OnePlus 13 (dodge) SM8750 Linux bringup

Main branch for this repo work: `oneplus-13-sm8750-bringup-v2`.

Цель ветки: максимально расширить совместимость Linux kernel с OnePlus 13 на Snapdragon 8 Elite / SM8750, включая уже существующие наработки postmarketOS/DTBO/OnePlusOSS и данные из `boot.img`/ACPI/DTBO ветки `skb8/sm8750`.

## GitHub Actions build

Ветка содержит workflow `.github/workflows/oneplus13-kernel.yml`. Он собирает:

- `arch/arm64/boot/Image.gz`
- `arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dtb`
- итоговый `.config`

Артефакт называется `oneplus13-sm8750-kernel`.

## Что было извлечено из boot.img / sm8750 ACPI work

`boot.img` в `skb8/sm8750`:

- commit: `c92aeb790bc4cfd5d8a6867553c4f06fc5680eaf`
- blob SHA: `58e10eccade5eed50f7ae5c614ed77d041b752c4`
- size: `100663296`

Практические выводы уже перенесены в ядро/доки:

| Блок | Вытащено | Что добавлено здесь |
| --- | --- | --- |
| USB | DWC3 `0x0a600000`, IRQ SPI 133, pwr IRQ SPI 130, eUSB2 PHY `0x088e3000`, QMP USB3/DP PHY `0x088e8000`, role OTG, super-speed-plus | USB/DWC3/NCM/PMIC-GLINK/UCSI/QMP configs |
| Display | splash fb `0xfc800000`, size `0x2b00000`, 1440x3168, panel reset GPIO98, backlight GPIO100, panel candidates AA545/BF262/AA569 | simplefb DTS, display notes, DRM/MSM configs |
| Touch | `synaptics_tcm_hbp@0`, `S3910`, firmware `AA545`, SPI `a90000`, IRQ GPIO162, reset GPIO161, AVDD PM8550VS_J GPIO3, VDD L4B | live touch node in DTS, `CONFIG_TOUCHSCREEN_SYNAPTICS_TCM_HBP=m` |
| Wi-Fi | WCN7850 on PCIe0, PARF `0x01c00000`, ECAM `0x40100000`, PERST GPIO102, WAKE GPIO104, WLAN_EN GPIO16 | PCIe/QMP PCIe/ath12k configs and boot findings doc |
| Battery | Oplus mms wired, virtual buck/gauge, capacity 5610/5920 mAh, USB temp ADCs `0x74a/0x75e`, charger UART GPIO62/63 | PMIC GLINK battery path kept, charger details documented |
| Thermals | PM8010/PM8550 temp alarms, PM8550 BCL `0x4700`, shell thermals | Qualcomm SPMI ADC/TM/temp configs and boot findings doc |
| Hall/cover | I2C `9a4000`, hall GPIO97, magnetic cover GPIO65 | documented as next DTS target |

Полный перенос деталей лежит в `Documentation/arm64/oneplus13-bootimg-findings.rst`.

## Легенда поддержки

| Значок | Значение |
| --- | --- |
| ✅ | должно работать или уже включено в live DTS/config |
| 🟨 | частично работает / нужен тест на устройстве |
| 🧪 | железо подтверждено, но нужен порт драйвера или сборка внешнего модуля |
| ❌ | пока не работает |

## Таблица совместимости

| Подсистема | Статус | Как реализовано / как будет работать | Нюансы |
| --- | --- | --- | --- |
| Boot | ✅ | Добавлен `arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts`, включён `CONFIG_ARM64_APPENDED_DTB` | Root dump подтвердил downstream target `sun-mtp,dodge`, project `23821` |
| CPU | ✅ | SM8750 DTSI описывает 8 Oryon CPU, включены `CONFIG_NR_CPUS=8` и `CONFIG_SCHED_CLUSTER` | Android грузится с performance governor, cpufreq/idle надо тестировать |
| RAM | ✅ | В DTS перенесён OnePlus 13 memory layout из sm8750-mainline dodge | Dump показывает managed memory около 11.3 GiB из-за carveouts |
| UFS storage | ✅ | Включены `CONFIG_SCSI_UFS_QCOM`, `CONFIG_SCSI_UFS_BSG`, `CONFIG_SCSI_UFS_CRYPTO`, inline encryption | Boot device подтверждён: `soc/1d84000.ufshc` |
| Display early boot | ✅ | `simple-framebuffer` 1440x3168, base `0xfc800000`, size `0x2b00000`, `a8r8g8b8` | Dump подтвердил splash region at `0xfc800000` |
| Display panel | 🧪 | Panel name confirmed: `AA569_P_3_A0019_dsc_cmd`; reset GPIO98 and backlight GPIO100 documented from boot/dtbo notes | Нужен полноценный panel driver payload/timings for AA569 |
| USB gadget | ✅ | Включён `CONFIG_USB_G_NCM` для раннего SSH по USB | Android bootconfig confirms controller `a600000.dwc3` |
| USB Type-C | ✅ | PMIC GLINK/UCSI включены, power_supply показывает `C`, `PD`, `PD_PPS` | boot/dtbo notes confirm DWC3 OTG and QMP USB3/DP combo PHY resources |
| Buttons | ✅ | Volume Down через PM8550 GPIO6, `gpio-keys`; PMIC PON handles pwrkey/resin | Dump confirms `gpio-keys`, `pmic_pwrkey`, `pmic_resin` inputs |
| Touchscreen | ✅ | В DTS добавлен рабочий `synaptics_tcm_hbp@0` на `&spi4` / `a90000.spi`, IRQ GPIO162, reset GPIO161, AVDD PM8550VS_J GPIO3, VDD `vreg_l4b_1p8`, firmware `AA545` | Нужен драйвер `synaptics_tcm_hbp/synaptics_tcm2`; config symbol добавлен как module |
| Fingerprint | 🧪 | Touch node оставляет `fingerprint_not_report_in_suspend`; dump confirms `oplus_fp_input` | Требует touch sysfs + fingerprint userspace |
| Battery / gauge | 🧪 | Battery power_supply works on Android, full/design `5920000`, boot notes confirm 5610/5920 mAh and bq/Oplus virtual gauge path | Basic PMIC GLINK battery first, VOOC/Oplus gauge needs vendor stack |
| Wired charging | 🧪 | PMIC GLINK battery_charger, USB power_supply and Oplus ADSP charger logs confirmed; boot notes add USB temp ADCs and charger UART GPIO62/63 | PD/PPS basic path likely easiest, VOOC/UFCS needs Oplus framework |
| Wireless charging / OTG boost | 🧪 | Wireless power_supply exists, currently not present | Downstream WLS nodes are vendor-specific |
| Thermals | ✅ | Thermal zones confirmed; boot notes add PM8010/PM8550 temp alarms and PM8550 BCL register data | Shell thermal and PM8550 GPIO2 are high-confidence DTS targets |
| NFC | 🧪 | Android platform exposes `soc:nfc_chipset` and `soc:st54spi_gpio` | Target is likely ST54/ST NFC over SPI/GPIO, not generic PN544 assumption |
| Sensors | 🧪 | Confirmed tof8801 at I2C `5-0041`, hall tri-state, magnetic cover, SSC feedback | boot notes add hall GPIO97 and magnetic cover GPIO65 |
| IR blaster | 🧪 | Downstream IR remains QUPv3 SE5 SPI, dump exposes SPI controllers `spi0.0` and `spi1.0` | Need identify which `spi1.0` maps to IR before live enable |
| Cameras | ❌ | Camera/CVP/CDSP carveouts and thermal zones exist | Blocked by downstream Qualcomm/Oplus camera stack |
| Audio | 🧪 | Dump confirms `sun-mtp-snd-card`, WCD939x codec, RX/TX/VA/WSA macros, SoundWire aliases | Need WCD939x/LPASS driver support in this kernel tree |
| WLAN / BT | 🟨 | WCN7850 PCIe resources from boot notes, ath12k/QCA configs added | Need DTS labels/enablement for PCIe0/WLAN once SM8750 DTSI labels are stable |
| Modem / IPA | 🟨 | Android exposes `4080000.remoteproc-mss`, IPA at `3e00000.qcom,ipa`, rmnet-ipa | Userspace firmware/rmtfs/qmi still required |
| postmarketOS basics | ✅ | dm-crypt, Btrfs, F2FS, zram, WireGuard, binderfs, PSI, UTF-8, NCM | Practical base for rootfs, containers and debugging |

## OnePlus 13 downstream IDs

Root dump подтвердил, что конкретное устройство использует project ID `23821`, product/model `OP5D0DL1` / `PJZ110`, `dtbo_idx=5`, `dtb_idx=2`. Downstream overlay для него: `dodge-23821-sun-overlay.dts`.
