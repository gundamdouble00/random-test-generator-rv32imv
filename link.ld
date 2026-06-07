ENTRY(main)

MEMORY
{
    text_mem(rx) : ORIGIN = 0x20000000, LENGTH = 33K
    data_mem (rwx) : ORIGIN = 0x12000000, LENGTH = 17K
}
SECTIONS
{
    .text : { *(.text) } > text_mem

    .data : { *(.data) *(.sdata) } > data_mem

    .tohost : {
        . = ALIGN(8);
        KEEP(*(.tohost))
        . = ALIGN(8);
    } > data_mem
}