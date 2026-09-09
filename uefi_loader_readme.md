# Doda UEFI Loader Exploration

This directory contains research and an initial bootloader stub representing the frontier of DOS development: **Booting real-mode DOS natively on modern UEFI systems without a Compatibility Support Module (CSM).**

## The Problem

Modern PCs have entirely dropped BIOS and CSM support. They boot directly via UEFI into 32-bit or 64-bit protected/long mode. MS-DOS is a 16-bit real-mode operating system that relies *exclusively* on legacy BIOS interrupts (like `INT 10h` for video and `INT 13h` for disk access) to function. Without these interrupts, the DOS kernel cannot output text to the screen or read from the drive.

## The Exploration Path

To run a native DOS fork on pure UEFI hardware, the bootloader must bridge the gap. We are exploring two potential architectures to solve this in the future:

1.  **Software Emulation Layer:** The UEFI loader sets up memory and boots a minimal hypervisor or emulator (like an embedded DOSBox or v86 instance), which then boots the actual DOS kernel inside an emulated legacy environment.
2.  **In-Memory BIOS Emulation (Mini-CSM):** The UEFI loader sets up a Virtual 8086 mode (V86) monitor, writes translation wrappers for standard `INT` calls (translating them to UEFI protocol calls in the background), and drops the CPU back into real mode before executing the DOS kernel.

## Compiling the Stub

The provided `efi_main.c` is a native EFI application stub built using `gnu-efi`. It prints diagnostics directly to the UEFI firmware console before halting, representing step zero of the journey.

```bash
cd uefi_loader
make
```
*(Requires `gnu-efi` development packages installed on your Linux build machine).*
