# OnePlus 13 (dodge) SM8750 Linux bringup

Main branch for this repo work: `oneplus-13-sm8750-bringup-v2`.

Цель ветки: максимально расширить совместимость Linux kernel с OnePlus 13 на Snapdragon 8 Elite / SM8750, не ломая boot мусорным downstream-копипастом. Всё, что уже безопасно для mainline-style ядра, включается в DTS/config. Всё, что пока завязано на vendor-only Oplus драйверы, размечается как hardware map и портируется отдельными шагами.

## Легенда поддержки

| Значок | Значение |
| --- | --- |
| ✅ | должно работать или уже включено в live DTS/config |
| 🟨 | частично работает / нужен тест на устройстве |
| 🧪 | железо размечено, но нужен порт драйвера или аккуратная проверка |
| ❌ | пока не работает в mainline-ядре |
| ❓ | нужны значения с устройства |

## Источники

| Источник | Что взято |
| --- | --- |
| `sm8750-mainline/linux`, `OnePlus-13-WIP` @ `1f2047e8663eda76c8b172fd3e040e3b3fa17950` | стартовый OnePlus 13 DTS, memory map, simple-framebuffer, ранний bringup, USB/NCM |
| `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`, `oneplus/sm8750_b_16.0.0_oneplus_13` @ `0de73fc272a09a1e12e4e758a4d17ae7108df7fc` | downstream hardware map: touch, charger, NFC, sensors, IR, display overlays, project IDs |
| `skb8/sm8750`, `feat/sm8750-acpi-madt-gtdt`, `dtbo.img` @ `572295afe95ae2350d4a2b9872fed5d1d91a3195` | универсальный DTBO источник для сверки OnePlus 13 overlays, blob SHA `240c20b2649d3daafa4abb7109fd316cd28febd2` |

## Таблица совместимости

| Подсистема | Статус | Как реализовано / как будет работать | Нюансы |
| --- | --- | --- | --- |
| Boot | ✅ | Добавлен `arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts`, включён `CONFIG_ARM64_APPENDED_DTB` | Нужно проверить boot с реальным Image.gz+dtb |
| CPU | ✅ | SM8750 DTSI описывает 8 Oryon CPU, включены `CONFIG_NR_CPUS=8` и `CONFIG_SCHED_CLUSTER` | Нужен тест cpufreq/idle на железе |
| RAM | ✅ | В DTS перенесён OnePlus 13 16 GB layout из sm8750-mainline dodge | Для 12/24 GB SKU сверять DTBO/bootloader memory map |
| UFS storage | ✅ | Включены `CONFIG_SCSI_UFS_QCOM`, `CONFIG_SCSI_UFS_BSG`, `CONFIG_SCSI_UFS_CRYPTO`, inline encryption | Должно дать rootfs/storage, нужен boot test |
| Filesystem encryption | ✅ | `CONFIG_FS_ENCRYPTION`, inline crypto, dm-crypt, F2FS/Btrfs | Подходит для pmOS userdata/rootfs экспериментов |
| Display early boot | ✅ | `simple-framebuffer` 1440x3168, base `0xfc800000`, size `0x2b00000`, `a8r8g8b8` | Это ранняя картинка, не полноценный display driver |
| Display DRM/MSM | 🟨 | Включены SM8750 display/GPU clocks и `CONFIG_DRM_MSM` | Панель OnePlus 13 ещё надо вынести из downstream display overlay |
| GPU | 🟨 | Включён `CONFIG_SM_GPUCC_8750`, DRM/MSM path подготовлен | Нужны firmware и проверка Adreno binding |
| USB gadget | ✅ | Включён `CONFIG_USB_G_NCM` для раннего SSH по USB | Serial gadget выключен, NCM полезнее для bringup |
| USB Type-C | 🟨 | Включены PMIC GLINK/UCSI, добавлен `pmic-glink` node | ❓ Нужен orientation/role GPIO или подтверждение, что PMIC GLINK сам справляется |
| Buttons | ✅ | Volume Down через PM8550 GPIO6, `gpio-keys` | Power обычно через PMIC PON, не отдельная gpio-key |
| Touchscreen | 🧪 | Downstream: Synaptics S3910 / `synaptics,tcm-spi-hbp` на QUPv3 SE4 SPI, IRQ GPIO162, reset GPIO161, AVDD PM8550VS_J GPIO3, VDD `L4B` | Не включено live: HBP/Oplus touch stack не mainline-ready |
| Fingerprint | 🧪 | Touch overlay содержит underscreen fingerprint flags и suspend/report нюансы | Требует рабочий touch stack и отдельный fingerprint userspace/driver путь |
| Battery / gauge | 🧪 | Downstream: 5610 mAh, dual battery, virtual gauge, ADSP gauge, PM8550 charger | Live включён generic PMIC GLINK path, Oplus charger framework не портирован |
| Wired charging | 🧪 | Downstream: PD/QC/VOOC/UFCS limits, PM8550 buck, USB temp ADC, discharge GPIO | Нельзя просто включить vendor framework, нужен mainline-safe зарядный путь |
| Wireless charging / OTG boost | 🧪 | Downstream содержит RX/CP groups, OTG boost GPIO, WLS/non-coexistence hints | Нужен отдельный порт, иначе будет dead DT |
| Thermals | 🧪 | PM8550 GPIO2 thermistor, shell front/frame/back thermal nodes найдены | Можно портировать после проверки ADC channel names на устройстве |
| Flash / torch | 🧪 | Downstream ставит PM8550 flash0-3 и torch0-3 `qcom,ires-ua = <5000>` | Можно включать после сверки PMIC LED nodes в текущем tree |
| NFC | 🧪 | Есть `oplus_nfc/dodge_nfc.dtsi` в OnePlusOSS | Нужны compatible/reg/irq из девайса и mainline NFC driver match |
| Sensors | 🧪 | SSC feedback, sensor devinfo, mag fusion, hall sensor GPIO97, magnetic cover GPIO65 | Oplus sensor stack private, но GPIO/I2C/SPI карта готова |
| IR blaster | 🧪 | `oplus,kookong_ir_spi` на QUPv3 SE5 SPI, MOSI GPIO53, 5 MHz, regulator `pm_humu_l9` | Добавлен config для generic SPI/RC userspace экспериментов |
| Cameras | ❌ | Camera/CVP/CDSP reserved memory есть в SoC tree | Камеры завязаны на downstream Qualcomm/Oplus camera stack |
| Audio | ❓ | Добавлены базовые sound configs для следующего шага | Нужны codec/LPASS/SoundWire nodes и firmware names |
| WLAN | 🟨 | Добавлены ath12k/cfg80211/mac80211 configs | ❓ Нужны board files/calibration, PCIe path, firmware names |
| Bluetooth | 🟨 | Добавлены BT/QCA configs | ❓ Нужны UART/firmware details из Android/sysfs |
| Modem / IPA | 🟨 | MPSS/IPA memory regions есть в базовом SM8750 DTSI, включены RMTFS/RPMSG basics | Требуется userspace firmware/rmtfs/qmi/ModemManager path |
| LEDs | 🟨 | Включены LED triggers, multicolor, LPG, flash class | Нужны live nodes после сверки PMIC LED topology |
| postmarketOS basics | ✅ | dm-crypt, Btrfs, F2FS, zram, WireGuard, binderfs, PSI, UTF-8, NCM | Практичный набор для rootfs, контейнеров и отладки |

## Что уже добавлено в live DTS/config

- OnePlus 13 DTS skeleton with SM8750 + PMIC includes.
- 16 GB memory map from dodge bringup tree.
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

Downstream overlay `dodge-23893-sun-overlay.dts` указывает project IDs `23893`, `23894`, `23895`. Hardware IDs: `T1`, `EVT1`, `EVT2`, `DVT1`, `DVT2`, `PVT1`.

## Что нужно узнать с root-устройства

Запусти на Android/root shell скрипт из репозитория:

```sh
su
sh tools/oneplus13-collect-device-info.sh > /sdcard/oneplus13-device-info.txt 2>&1
```

И пришли файл `oneplus13-device-info.txt`. Самые важные данные: `/proc/device-tree/model`, compatible, chosen bootargs, reserved memory, panel name, touchscreen SPI/I2C node, NFC node, PMIC GLINK/Type-C nodes, battery/charger power_supply, WLAN/BT firmware names.

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
grep -RniE 'dodge|23893|23894|23895|oneplus|CPH2649|CPH2653|CPH2655|PJZ110' out/dtbo
```

## Следующие порты по приоритету

1. ✅ Проверить boot с appended DTB и simplefb.
2. ✅ Проверить UFS/rootfs, USB NCM и PMIC GLINK Type-C.
3. 🧪 Портировать touchscreen S3910 минимально: SPI, GPIO162 IRQ, GPIO161 reset, питание.
4. 🧪 Добавить безопасные thermals/LED/flash nodes.
5. 🧪 Разобрать NFC и sensors после root dump.
6. 🧪 После этого идти в battery/charger, audio, WLAN/BT.
