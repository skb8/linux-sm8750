#!/system/bin/sh
# Collect useful OnePlus 13 (dodge) root-side data for mainline Linux bringup.
# Run on Android as root:
#   su
#   sh tools/oneplus13-collect-device-info.sh > /sdcard/oneplus13-device-info.txt 2>&1

set +e

section() {
    echo
    echo "===== $* ====="
}

cat_file() {
    f="$1"
    if [ -e "$f" ]; then
        echo "--- $f"
        cat "$f" 2>/dev/null | tr '\0' '\n'
    fi
}

list_dir() {
    d="$1"
    if [ -d "$d" ]; then
        echo "--- $d"
        ls -la "$d" 2>/dev/null
    fi
}

section "uname / android props"
uname -a
getprop ro.product.device
getprop ro.product.model
getprop ro.boot.hardware
getprop ro.boot.hw_version
getprop ro.boot.prjname
getprop ro.boot.project_name
getprop ro.boot.rf_version
getprop ro.boot.serialno
getprop ro.boot.dynamic_partitions
getprop ro.boot.slot_suffix

section "proc cmdline"
cat_file /proc/cmdline
cat_file /proc/bootconfig

section "device-tree identity"
cat_file /proc/device-tree/model
cat_file /proc/device-tree/compatible
cat_file /proc/device-tree/chosen/bootargs
cat_file /proc/device-tree/chosen/stdout-path
cat_file /proc/device-tree/chosen/framebuffer/reg
cat_file /proc/device-tree/chosen/framebuffer/width
cat_file /proc/device-tree/chosen/framebuffer/height
cat_file /proc/device-tree/chosen/framebuffer/stride
cat_file /proc/device-tree/chosen/framebuffer/format

section "device-tree aliases"
find /proc/device-tree/aliases -maxdepth 1 -type f -print -exec sh -c 'echo -n " = "; tr "\0" "\n" < "$1"' _ {} \; 2>/dev/null

section "reserved memory"
find /proc/device-tree/reserved-memory -maxdepth 2 -type f -name reg -print -exec sh -c 'echo "--- $1"; od -An -tx4 "$1"' _ {} \; 2>/dev/null

section "memory nodes"
find /proc/device-tree -maxdepth 2 -type d -name 'memory*' -print 2>/dev/null
find /proc/device-tree -maxdepth 2 -type f -path '*/memory*/reg' -print -exec sh -c 'echo "--- $1"; od -An -tx4 "$1"' _ {} \; 2>/dev/null

section "display / panel clues"
find /proc/device-tree -iname '*panel*' -o -iname '*dsi*' -o -iname '*display*' 2>/dev/null | head -200
find /proc/device-tree -type f \( -name compatible -o -name label -o -name qcom,mdss-dsi-panel-name \) -print 2>/dev/null | while read f; do
    v=$(tr '\0' '\n' < "$f" 2>/dev/null)
    echo "$f: $v" | grep -Ei 'panel|dsi|display|mdss|aa545|aa569|bf262'
done

section "touchscreen / input clues"
find /proc/device-tree -type f \( -name compatible -o -name reg -o -name interrupts -o -name '*gpio*' \) -print 2>/dev/null | while read f; do
    p=$(echo "$f" | grep -Ei 'touch|synaptics|goodix|tcm|spi@|i2c@')
    [ -n "$p" ] && { echo "--- $f"; od -An -tx4 "$f" 2>/dev/null || cat "$f" 2>/dev/null | tr '\0' '\n'; }
done
list_dir /dev/input
cat /proc/bus/input/devices 2>/dev/null

section "nfc clues"
find /proc/device-tree -type f \( -name compatible -o -name reg -o -name interrupts -o -name '*gpio*' \) -print 2>/dev/null | while read f; do
    echo "$f" | grep -Eiq 'nfc|pn5|sn100|nqx|ese' || continue
    echo "--- $f"
    od -An -tx4 "$f" 2>/dev/null || cat "$f" 2>/dev/null | tr '\0' '\n'
done

section "battery / charger / type-c"
for d in /sys/class/power_supply/*; do
    [ -d "$d" ] || continue
    echo "--- $d"
    for f in type present online status capacity voltage_now current_now charge_full charge_full_design temp technology usb_type scope model_name manufacturer; do
        [ -e "$d/$f" ] && echo "$f=$(cat "$d/$f" 2>/dev/null)"
    done
done
find /proc/device-tree -type f -path '*pmic*' -o -path '*charger*' -o -path '*battery*' -o -path '*typec*' 2>/dev/null | head -200

section "wlan / bluetooth firmware clues"
dmesg 2>/dev/null | grep -Ei 'ath12k|wcn|qca|bluetooth|bt|firmware|board-2|cal' | tail -300
find /vendor/firmware /vendor/firmware_mnt /odm/firmware /lib/firmware -maxdepth 3 -type f 2>/dev/null | grep -Ei 'ath12k|wcn|qca|board|bdf|amss|m3|bt|nvm' | head -300

section "audio clues"
find /proc/device-tree -type f \( -name compatible -o -name model -o -name sound-name-prefix \) -print 2>/dev/null | while read f; do
    v=$(tr '\0' '\n' < "$f" 2>/dev/null)
    echo "$f: $v" | grep -Ei 'audio|sound|wcd|lpass|swr|soundwire|tx-macro|rx-macro|va-macro'
done
ls -la /proc/asound 2>/dev/null
cat /proc/asound/cards 2>/dev/null

section "i2c / spi / platform devices"
ls -la /sys/bus/i2c/devices 2>/dev/null
ls -la /sys/bus/spi/devices 2>/dev/null
ls -la /sys/bus/platform/devices 2>/dev/null | grep -Ei 'qup|spi|i2c|pmic|glink|ucsi|typec|nfc|touch|panel|dsi|gpu|kgsl|ipa|remoteproc|audio|wcd|lpass' | head -300

section "gpio labels if available"
for d in /sys/kernel/debug/gpio /d/gpio; do
    [ -e "$d" ] && cat "$d"
done

section "thermal zones"
for z in /sys/class/thermal/thermal_zone*; do
    [ -d "$z" ] || continue
    echo "--- $z"
    [ -e "$z/type" ] && cat "$z/type"
    [ -e "$z/temp" ] && cat "$z/temp"
done

section "dtbo / partitions"
ls -la /dev/block/by-name 2>/dev/null | grep -Ei 'dtbo|boot|vendor_boot|init_boot|modem|bluetooth|dsp|abl|xbl'

section "done"
