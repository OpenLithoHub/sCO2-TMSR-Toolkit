"""PCHE reduced-order model (ROM) — training, evaluation, and FMU export.

Reference: docs/02_phase2_cfd_rom.md § 2.6.

Sub-modules:
    train_rom              — train an MLP on the CFD dataset, export ONNX.
    dataset.extract_from_cfd — parse OpenFOAM run dirs into training_set.csv.
    exported.wrap_as_fmu    — wrap the trained ONNX as an FMI 2.0 FMU for Modelica.
"""
