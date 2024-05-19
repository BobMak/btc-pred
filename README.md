
# BitSmart

CMPE 257 Project, by Group 2:
Alexander Iakovlev, Pratik Korat, Volodymyr Makarenko

## Installation

install tensorflow with cuda backend if you are using an Nvidia GPU
`pip install -r requirements-gpu.txt`

install tensorflow with cpu backend if you are using a CPU
`pip install -r requirements-cpu.txt`

Download the [BTC-USD Dataset](https://drive.google.com/file/d/13fxWREs-b4YxLYZnqMvvsYXcFGT_LqbT/view?usp=sharing)  
Download [models](https://drive.google.com/drive/folders/1dJltpgLW0Q6DY-B3LvmTbXhdIR9PoZ5k?usp=sharing) into `models` directory

## Training

Use `notebooks/Data Modelling.ipynb` to pre-process the data and train the models

## Inference

we are using streamlit for user interface. 
Run the `streamlit run deployment/deploy.py` to start the ui with the model.
Will try to use the `gru1.keras` model by default, if you'd like to set a different model, set the path as an environment variable:
`MODEL_PATH=models/gru1.keras streamlit run deployment/deploy.py`

## Live demo

Deployed at: http://cmpe257-group2.ddnsfree.com:8501/ (http://24.6.123.142:8501/)