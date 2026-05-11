# Conda Environment Setup

## Environment

| Setting | Value |
|---|---|
| Name | `electrode_mapper` |
| Python | 3.10.16 |
| PyQt5 | 5.15.11 |
| PyQtGraph | 0.13.7 |
| NumPy | 2.2.6 |

---

## Quick Reference

```bash
# Activate
conda activate electrode_mapper

# Deactivate
conda deactivate

# Run the app
conda activate electrode_mapper
python main.py
```

---

## Create from Scratch

```bash
conda create -n electrode_mapper python=3.10 -y
conda activate electrode_mapper
conda install -c conda-forge pyqt pyqtgraph numpy -y
```

---

## Remove Environment

```bash
conda deactivate
conda env remove -n electrode_mapper
```
