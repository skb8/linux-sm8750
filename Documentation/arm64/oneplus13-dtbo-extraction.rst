OnePlus 13 dtbo.img extraction notes
====================================

The reference DTBO image is stored in ``skb8/sm8750`` on branch ``feat/sm8750-acpi-madt-gtdt``:

* file: ``dtbo.img``
* commit: ``572295afe95ae2350d4a2b9872fed5d1d91a3195``
* blob SHA: ``240c20b2649d3daafa4abb7109fd316cd28febd2``
* size: ``25165824`` bytes

Use this locally to split and decompile it:

.. code-block:: sh

   git clone https://github.com/skb8/sm8750.git
   cd sm8750
   git checkout feat/sm8750-acpi-madt-gtdt

   mkdir -p out/dtbo
   mkdtimg dump dtbo.img -b out/dtbo/dtbo
   for dtb in out/dtbo/*.dtb; do
       dtc -I dtb -O dts -o "${dtb%.dtb}.dts" "$dtb"
   done

Then grep for OnePlus 13 / dodge identifiers:

.. code-block:: sh

   grep -RniE 'dodge|23893|23894|23895|oneplus|CPH2649|CPH2653|CPH2655|PJZ110' out/dtbo

Only merge overlays that match the OnePlus 13 IDs.  The DTBO image is shared across multiple SM8750 devices, so treating every overlay as dodge-specific is wrong and will make the kernel worse, not better.
