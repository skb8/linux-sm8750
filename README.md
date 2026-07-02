# OnePlus 13 (dodge) SM8750 Linux bringup

Эта ветка собирает mainline-oriented bringup для OnePlus 13 на Snapdragon 8 Elite / SM8750. Цель: максимально расширить совместимость ядра с телефоном, но не тащить downstream-only Oplus-ноды вслепую, если под них нет mainline-драйвера.

## Источники

| Источник | Что взято |
| --- | --- |
| `sm8750-mainline/linux`, `OnePlus-13-WIP` @ `1f2047e8663eda76c8b172fd3e040e3b3fa17950` | базовый OnePlus 13 DTS, память, simple-framebuffer, ранний bringup, USB/NCM идея |
| `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`, `oneplus/sm8750_b_16.0.0_oneplus_13` @ `0de73fc272a09a1e12e4e758a4d17ae7108df7fc` | downstream hardware map: touch, charger, NFC, sensors, IR, display overlays, project IDs |
| `skb8/sm8750`, `feat/sm8750-acpi-madt-gtdt`, `dtbo.img` @ `572295afe95ae2350d4a2b9872fed5d1d91a3195` | универсальный DTBO источник для проверки OnePlus 13 overlays, blob SHA `240c20b2649d3daafa4abb7109fd316cd28febd2` |

## Текущий статус совместимости

| Подсистема | Статус | Как реализовано / как должно работать | Нюансы |
| --- | --- | --- | --- |
| Boot | Улучшено | Добавлен `arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts`, включён `CONFIG_ARM64_APPENDED_DTB` | Makefile wiring ещё лучше сделать отдельным патчем, чтобы не сломать огромный qcom Makefile |
| CPU | Включено | SM8750 DTSI описывает 8 Oryon CPU, включён `CONFIG_NR_CPUS=8` и `CONFIG_SCHED_CLUSTER` | Нужна проверка частот/idle на железе |
| RAM | Улучшено | В DTS перенесён OnePlus 13 16 GB memory layout из sm8750-mainline dodge | Для других RAM SKU сверять DTBO/bootloader memory map |
| UFS storage | Включено | `CONFIG_SCSI_UFS_QCOM`, `CONFIG_SCSI_UFS_BSG`, `CONFIG_SCSI_UFS_CRYPTO`, inline encryption | Должно дать rootfs/storage, но нужен тест загрузки |
| Display early boot | Улучшено | `simple-framebuffer` 1440x3168, base `0xfc800000`, size `0x2b00000`, format `a8r8g8b8` | Это ранняя картинка, не полноценный DRM panel driver |
| Display DRM/MSM | Подготовлено | Включены SM8750 display/GPU clocks и `CONFIG_DRM_MSM` | Панель OnePlus 13 из downstream пока не портирована в mainline bindings |
| USB gadget | Улучшено | Включён `CONFIG_USB_G_NCM` для раннего SSH по USB | Serial gadget выключен, NCM полезнее для bringup |
| USB Type-C | Частично | Включены PMIC GLINK/UCSI, добавлен `pmic-glink` node | Downstream сам не даёт уверенный orientation GPIO, нужно проверить на железе |
| Кнопки | Улучшено | Volume Down через `pm8550_gpios` GPIO6, `gpio-keys` | Power обычно через PMIC PON, не отдельная gpio-key |
| Touchscreen | Размечено | Downstream: Synaptics S3910 / `synaptics,tcm-spi-hbp` на QUPv3 SE4 SPI, IRQ GPIO162, reset GPIO161, AVDD PM8550VS_J GPIO3, VDD `L4B` | Не включено live: downstream HBP/Oplus stack не mainline-ready |
| Fingerprint | Размечено | Touch overlay содержит underscreen fingerprint flags и suspend/report нюансы | Требует touch stack и отдельный fingerprint userspace/driver путь |
| Battery / gauge | Размечено | Downstream: 5610 mAh, dual battery, virtual gauge, ADSP gauge, PM8550 charger | Live включён generic PMIC GLINK path, Oplus charger framework не портирован |
| Wired charging | Размечено | Downstream: PD/QC/VOOC/UFCS limits, PM8550 buck, USB temp ADC, discharge GPIO | Не включено live, потому что Oplus charging framework vendor-only |
| Wireless / reverse charging | Размечено | Downstream содержит RX/CP groups и OTG/WLS boost GPIO hints | Нужен отдельный clean-room порт или mainline-compatible driver |
| Thermals | Размечено | PM8550 GPIO2 thermistor, shell front/frame/back thermal nodes в downstream | Можно портировать безопасные thermal zones после проверки ADC channel names |
| Flash / torch | Размечено | Downstream ставит PM8550 flash0-3 и torch0-3 `qcom,ires-ua = <5000>` | Можно включать после сверки PMIC LED nodes в текущем kernel tree |
| NFC | Размечено | Есть `oplus_nfc/dodge_nfc.dtsi` в OnePlusOSS | Нужно заменить/адаптировать private compatibles к mainline NFC driver |
| Sensors | Размечено | SSC feedback, sensor devinfo, mag fusion, hall sensor GPIO97, magnetic cover GPIO65 | Oplus sensor stack private, но GPIO/I2C/SPI карта полезна для порта |
| IR blaster | Размечено | `oplus,kookong_ir_spi` на QUPv3 SE5 SPI, MOSI GPIO53, 5 MHz, regulator `pm_humu_l9` | Нужен mainline IR driver или userspace SPI binding, сейчас только карта железа |
| Cameras | Reserved only | Camera/CVP/CDSP reserved memory есть в SoC tree | Камеры завязаны на downstream Qualcomm/Oplus camera stack, mainline нет |
| Audio | Не готово | В конфиге пока не включался полный LPASS/WCD path | Нужны codec, soundwire/LPASS nodes и проверка firmware |
| WLAN / BT | Подготовлено | Включены debug configs для ath12k/cfg80211/mac80211 и Bluetooth userspace basics | Нужны firmware/calibration и проверка PCIe/board data |
| Modem / IPA | Частично | MPSS/IPA memory regions есть в базовом SM8750 DTSI | Мобильная связь зависит от firmware, rmtfs, qmi/ModemManager и IPA path |
| LEDs | Подготовлено | Включены LED triggers, multicolor, LPG и flash class | Нужны live nodes после сверки PMIC LED topology |
| postmarketOS basics | Улучшено | dm-crypt, Btrfs, F2FS, zram, WireGuard, binderfs, PSI, UTF-8, NCM | Это практичный набор для rootfs, контейнеров и отладки |

## Почему не включены все downstream-ноды сразу

OnePlusOSS DTS содержит много `oplus,*` compatible strings. Если просто вставить их в live DTS, mainline kernel их не забиндит, а часть может мешать boot/probe. Поэтому в ветке сделано правильнее: безопасный live DTS плюс отдельная compatibility map для поэтапного порта.

## OnePlus 13 downstream IDs

Downstream overlay `dodge-23893-sun-overlay.dts` указывает project IDs `23893`, `23894`, `23895`. Hardware IDs: `T1`, `EVT1`, `EVT2`, `DVT1`, `DVT2`, `PVT1`.

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

## Практический порядок следующих портов

1. Проверить boot с appended DTB и simplefb.
2. Добить qcom Makefile entry для `sm8750-oneplus-dodge.dtb`.
3. Проверить UFS/rootfs, USB NCM и PMIC GLINK Type-C.
4. Портировать touchscreen S3910 минимально: SPI, GPIO162 IRQ, GPIO161 reset, питание.
5. Добавить безопасные thermals/LED/flash nodes.
6. После этого идти в battery/charger, NFC, sensors, audio, WLAN/BT.

