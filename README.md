# CNN_LSTM
 
How to get the data?
- https://bwsyncandshare.kit.edu/s/L5DcgekDWoT2m4R
- Build a './DATA' folder and put those .xls files in it

DataProcess_raw2vec.py
- First step of the project, convert raw data into the form that the following steps need.
- Build 2 folders './Vecs' and './Seps' before running this

Before Training
- After running DataProcess_raw2vec.py, build a folder './Models/Saved_Model'
- Build 2 folders './Seps/train' and './Seps/test', divide files in './Seps' randomly into these two folders

Training
- There are 5 models provided for comparation
- CNNLSTM_cnn.py: Vanilla CNN Model
- CNNLSTM_lstm.py: Vanilla LSTM Model
- CNNLSTM_fsw.py: Intraframe-CNN-LSTM Model
- CNNLSTM_osw.py: Interframe-CNN-LSTM Model
- CNNLSTM_nsw.py: Combi-CNN-LSTM Model
- The trained models will be saved in './Models/Saved_Model'
- For definations of the last 3 models, please refer to my master thesis "An Earable Interactive System Based on Head Motion Recognition from the Data Captured from IMUs" for more details

ResultFilter.py
- Including postprocessing steps (details in my thesis) and evaluation

ModelTransform.py
- Transform Tensorflow-Models into Tflite-Models, so that you can easily deploy this into any Android APP.
- Build a folder './tflite_models' before running this

quaternion.py, vector.py
- Including functions related to Quaternion Calculation and Vector Calculation
