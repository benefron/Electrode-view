# Conda Environment Setup

## Environment Name
`electrode_mapper`

## Activation
```bash
conda activate electrode_mapper
```

## Deactivation
```bash
conda deactivate
```

## Installed Packages
- Python 3.10.16
- PyQt5 (5.15.11)
- PyQtGraph (0.13.7)
- NumPy (2.2.6)

## Recreate Environment
If you need to recreate the environment on another machine:

```bash
# Create environment
conda create -n electrode_mapper python=3.10 -y

# Activate it
conda activate electrode_mapper

# Install packages
conda install -c conda-forge pyqt pyqtgraph numpy -y
```

## Remove Environment
If you need to remove the environment:

```bash
conda deactivate
conda env remove -n electrode_mapper
```

## Running the Application
```bash
conda activate electrode_mapper
python main.py
```
