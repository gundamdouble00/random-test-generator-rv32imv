ENTRY(main)

MEMORY
{
    text_mem(rx) : ORIGIN = 0x20000000, LENGTH = 33K
    data_mem (rwx) : ORIGIN = 0x22000000, LENGTH = 2K
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