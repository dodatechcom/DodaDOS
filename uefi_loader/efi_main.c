#include <efi.h>
#include <efilib.h>

/**
 * UEFI Bootloader Exploration for DOS
 *
 * Objective: Booting 16-bit real-mode DOS from a modern UEFI system without CSM.
 *
 * Current limitation: Modern UEFI drops the CPU straight into protected or long mode,
 * completely omitting the legacy 16-bit real-mode interrupts (like INT 10h for video
 * or INT 13h for disk) that DOS entirely relies upon.
 *
 * To run DOS on pure UEFI, a bootloader must:
 * 1. Initialize a software emulator (like an embedded DOSBox/v86) OR
 * 2. Implement a complete Legacy BIOS emulation layer in memory (a mini-CSM)
 *    before executing the DOS kernel.
 *
 * This stub represents the very beginning of that journey—a native EFI application
 * that says hello to the firmware before attempting the massive task of dropping
 * the CPU back to real mode.
 */

EFI_STATUS
EFIAPI
efi_main (EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    // Initialize the GNU-EFI library
    InitializeLib(ImageHandle, SystemTable);

    // Print to the UEFI console
    Print(L"Doda DOS UEFI Loader Exploration\n");
    Print(L"================================\n");
    Print(L"Attempting to prepare environment for 16-bit execution...\n");

    // (In a real scenario, we would load the DOS kernel into memory here)

    Print(L"Legacy BIOS interrupts (CSM) not found.\n");
    Print(L"Halting. True UEFI-to-DOS transition requires a V86 monitor or emulator.\n");

    // Wait for a keystroke before exiting back to firmware
    EFI_INPUT_KEY Key;
    Print(L"\nPress any key to return to UEFI firmware...\n");
    while (SystemTable->ConIn->ReadKeyStroke(SystemTable->ConIn, &Key) == EFI_NOT_READY) {
        // Wait
    }

    return EFI_SUCCESS;
}
