## Installation

install tensorflow with cuda backend if you are using an Nvidia GPU
`pip install -r requirements-gpu.txt`

install tensorflow with cpu backend if you are using a CPU
`pip install -r requirements-cpu.txt`

## Training

Use `notebooks/Data Modelling.ipynb` to pre-process the data and train the models

## Inference

we are using streamlit for user interface. 
Run the `streamlit run deployment/deploy.py` to start the ui with the model. 