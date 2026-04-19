# Printing Profiles Repository

This repository contains a collection of **3D printing profiles** and related project files for different printers, primarily:

- **Raise3D**
- **Prusa XL**

The goal of this repository is to keep printing settings organized, reusable, and easy to update across different materials, machines, and print objectives.

## What is included

The repository may include:

- Printer-specific profile files
- Material-specific slicing settings
- Project files used to prepare prints
- Example configurations for validated print setups

These files can be used as starting points for future prints and adapted depending on geometry, material behavior, layer height, speed, extrusion settings, and other process requirements.

## Example files

Examples of project and profile files have been uploaded, including:

- `30D-Raise.bin`
- `Flex_Pla_Prusa.3mf`

These examples illustrate how profiles and project files are organized for different printers and print conditions.

## Suggested repository organization

A typical structure for this repository could be:

```text
Raise3D/
  ├── Profiles/
  ├── Materials/
  └── Projects/

Prusa_XL/
  ├── Profiles/
  ├── Materials/
  └── Projects/
```

## Notes

- Profiles may need adjustment depending on nozzle size, filament brand, part geometry, and printer condition.
- Project files may reference specific print settings that were tuned for a particular part or experiment.
- It is recommended to document any important profile modifications directly in the repository when new settings are validated.

## Purpose

This repository serves as a centralized reference for tested and in-progress printing configurations, helping maintain consistency and making it easier to reproduce successful prints on both **Raise3D** and **Prusa XL** systems.
