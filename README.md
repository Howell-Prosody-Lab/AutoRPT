
---
# AutoRPT: Automatic Rapid Prosody Transcription Tool

**AutoRPT** is a Python command-line tool designed to automatically annotate prosodic features following the Rapid Prosody Transcription (RPT) protocol. It is currently trained on Standard American English (SAE), with future updates planned to include other language varieties.

### About the Project

This project is being developed by a team of undergraduate and graduate students, led by **PI Associate Professor Jonathan Howell** at **Montclair State University**. It is produced in conjunction with research funded by **NSF grant 2316030**, focusing on identifying the prosodic features of **“Three Varieties of English in NJ”**. The tool is designed to streamline the annotation of prosodic events using **Rapid Prosodic Transcription (RPT)**, as outlined by **Cole et al. (2017)**.

### Two Versions

There is both an AutoRPT and an AutoRPT_LSTM folder. The AutoRPT folder runs on a Recurrent Neural Network (RNN) framework and is more focused on the automatic annotation of prosodic events. The LSTM folder runs a Long Short-Term Memory (LSTM) framework and is more focused on the bootstrapping of annotations so that they can be reviewed by human annotators.

### Why We Built This Tool

1. **Limited Corpora for Specific Varieties**: Few corpora (with the exception of **CORAAL**) include **African American English (AAE)** and **Latine English (LE)**.
2. **Lack of Prosodic Annotations**: Even fewer corpora provide prosodic annotations for these varieties of English.
3. **Incomplete Annotation Schemes**: Current annotation schemes often do not account for the unique prosodic features of AAE and LE.
4. **Challenges in Crowdsourcing**: Annotating prosody through crowdsourcing methods can be difficult and inconsistent.

### Corpus and Training

AutoRPT is currently trained on the **Boston University Radio Corpus**, which serves as the foundation for the tool’s prosodic annotations. As research progresses, the model will be adapted to annotate prosodic features in other varieties of English, including those spoken in New Jersey.

### Prosodic Event Annotation and Detection in Three Varieties of English

AutoRPT is part of ongoing research into the detection of prosodic events across the following varieties (as spoken in New Jersey):

- **Mainstream American English (MAE)**
- **African American English (AAE)**
- **Latine English (LE)** 

---

## Installation Instructions

To run AutoRPT, you'll need to install several Python libraries. Follow the steps below to set up the tool on your system.

### Prerequisites

1. Ensure that you have Python version 3.7 or higher. You can download the latest version of Python [here](https://www.python.org/downloads/).
2. Download and unzip a copy of the repo.
3. It is recommended to create a virtual environment to manage the dependencies specific to AutoRPT.

### Step 1: Create a Virtual Environment (Optional but Recommended)

Setting up a virtual environment ensures that package installations for AutoRPT do not interfere with other Python projects on your machine. Use the command line/terminal to run the following script:

#### For Windows:
```bash
python -m venv AutoRPT
AutoRPT\Scripts\activate
```

#### For macOS/Linux:
```bash
python3 -m venv AutoRPT
source AutoRPT/bin/activate
```

### Step 2: Install Dependencies

Navigate to the directory containing the AutoRPT folder (this may be in your Downloads unless you have since moved it). Navigate into the AutoRPT-main\AutoRPT-main folder (you should be able to see `requirements.txt` when you open the folder in the system explorer or use DIR). 
You can install the required dependencies by running:

```bash
pip install -r requirements.txt
```

This command will install all the necessary Python packages listed in the `requirements.txt` file.

#### Required Python Packages

The key dependencies for AutoRPT are:

1. **Praat-ParselMouth**: A Python interface to Praat for conducting phonetic analyses.
2. **TextGrid**: A library used to handle Praat TextGrid objects for annotating speech.
3. **Scikit-learn**: A widely-used library for machine learning tasks such as classification and regression.
4. **Pandas**: A powerful data manipulation and analysis library.
5. **PyTorch**: An open-source deep learning framework, used for building and training machine learning models.

#### Model Pipeline
Install the SpacY model pipeline.
```bash
python -m spacy download en_core_web_sm
```

### Step 3: Install the trained models

We recommend that you use the most recent version of the trained models for LSTM, which can be found at [the top level of this repo](https://github.com/Howell-Prosody-Lab/rpt-training/tree/main) 
1. Go to the AutoRPT-main/AutoRPT-main/AutoRPT_LSTM/Model_paths that is now on your computer.
2. Delete the files out of it.
3. Download the models from the provided link.
4. Put them into that folder.
5. Rename the models to Intensity_LSTM_model.h5 and Pitch_LSTM_model.h5.

### Step 4: Run AutoRPT

Choose whether you want to run the (RNN) AutoRPT or the AutoRPT_LSTM and navigate into that folder.
e.g.
```bash
cd AutoRPT-main/AutoRPT-main/AutoRPT_LSTM
```

#### LSTM:
You can then run AutoRPT with the following command:

```bash
python LSTM_RPT.py
```
A file selection window will appear prompting you to select your TextGrid file. Select a file and press Open. Another selection window will appear prompting you to select a WAV file. Select a file and press Open.

Return to the command line or terminal and follow the instructions. 
AutoRPT will then start processing and annotating prosodic features based on the input data.

---

#### AutoRPT:
Example of how to call the tool:
![](/AutoRPT/CMD_Use_Instructions/AutoRPTCMDEx.jpeg)
The example path is in green. Start typing after the >.
1. Remember to include 'python' before calling the AutoRPT.py file (This is highlighted in Light Blue in the image)
** All parameters are highlighted yellow in the image
** All manually entered file paths are highlighted orange in the image
2. Enter --textgrid and then inside either "" or '' include the path to the desired Textgrid file
3. Enter --wav and then inside either "" or '' include the path to the desired wav file
4. Enter --tier and then inside either "" or '' include the name of the target tier from the Textgrid file

In the general folder of AutoRPT there will be Pitch and Intensity CSVs, feel free to delete these as they are no longer of use.

Within the csv_outputs folder there will be 3 files (per Wav/Textgrid run). These are CSVs that contain the predictions of the model.

Within the tg_outputs folder there will be 3 files (per Wav/Textgrid run). These are Textgrids that contain the predictions of the model.


Step by Step CMD Example

C:\YourFilePath>cd AutoRPT
C:\YourFilePath\AutoRPT>python AutoRPT.py --textgrid "YourTextgridFile.TextGrid" --wav "YourWavFile.wav" --tier "YourTierName"

---
## Script Breakdown

#### LSTM_RPT
Requires: os, tkinter, praatio, sys, Clean_I_Model, Clean_P_Model, Utilities

Description: "Main" file. Opens a file dialog to select TextGrid and WAV files, creates tiers in the TextGrid in which it marks suspected boundary and prominence and labels them with confidence percentages.

Functions:
* select_files() - Opens a file dialog to select TextGrid and WAV files. Requests tier names from user. Returns file paths and tier names.
* main(Path Textgrid_path, Path Wav_file_path, String tier, String phone_tier) - Creates tiers and places prosody annotations and confidence degrees from RPT functions in them. Calls all the other main functions: Pitch.run, Intensity.run, model_join.dict_merge, CTG.create_textgrid, Point_Tier.phone_data, CTG.create_point_tier. No returns.

If __main__: calls select_files to get user input, passes that input to main.

#### Clean_I_Model

Requires: parselmouth, tgt, numpy, spacy, pandas, re, os, tensorflow.keras.models, sklearn.preprocessing, sys, csv, datetime

Description: Defines and runs a number of functions related to intensity measures. 

Class IntensityExtraction functions:
* getIntensity(self, Wav_file: [parselmouth.Sound object](https://parselmouth.readthedocs.io/en/latest/api/parselmouth.Sound.html#parselmouth.Sound). start_time: float, end_time: float) - Returns intensity as a [parselmouth.Intensity object](https://parselmouth.readthedocs.io/en/latest/api/parselmouth.Intensity.html) 
* getMaxIntensity(self, intensity_full: parselmouth.Intensity) - Returns maximum intensity of a file as a float.
* getMinIntensity(self, intensity_full: parselmouth.Intensity) - Returns minimum intensity of a file as a float.
* getSTDIntensity(self, intensity_full: parselmouth.Intensity) - Returns standard deviation of intensity of a file as a float.
* getAverageIntensity(self, intensity_full: parselmouth.Intensity) - Returns arithmetic mean of intensity of a file as a float.

Class FileProcessorIntensity functions:
* __init__(self) - Runs model by itself calling IntensityExtraction().
* iterateTextGridforIntensity(self, TextGrid_path: str, tier_name: str, Wav_file: parselmouth.Sound object) - Creates array Interval_data, iterates through intervals of specified TextGrid tier, and runs calculations. Returns dict interval_data, int error_count, and array error_arr. Calls all IntensityExtraction functions.

Class SpeakerNormalization functions:
N.B. For all of the below functions: interval_data is a dict mapping strings to arrays. arr is a string representing the dict key to select the array.
* fileMean(self, interval_data: dict, arr: str) - Takes arr and returns the average of the values
* fileStd(self, interval_data: dict, avg: float, arr: str) - Takes arr and average and returns Standard Deviation (Std) of the values
* fileMin(self, interval_data: dict, arr: str) - Takes arr and returns the minimum value
* fileMax(self, interval_data: dict, arr: str) - Takes arr and returns the maximum value
* zScoreAppend(self, interval_data: dict, avg: float, std: float, arr: str) - Takes arr, average, standard deviation and returns the dict with Z-score appended.
* getZScore(self, key: number, avg: float, std: float) - Takes a specific value and returns the Z-score.

Class IntensityFormatToInterval functions:
* dictToArr(self, arr: dict) - Converts dictionary to array.
* outputArr(self, arr: array) - Prints array.

Class IntensityFormatting functions:
* to_csv(self, data: array, csv_file: str [path]) - Creates CSV file out of array and saves it. No returns.

Class Context functions:
* contextWindow(self, complete_data: dictionary) - allows for only local context as opposed to the total context that the speaker normalization class would gather. 

Class POS functions:
* add_pos_column_with_pandas(self, input_csv: str [path], text_column_name: str="Text", new_column_name: str="POS ID's") - Generates POS tags from spaCy model and saves to provided CSV file.
* clean_column(self, input_csv: str [path]) - Keeps only the first number from part of speech IDs.
* extract_first_number(cell) - defined inside clean_column

Class Saved_Model functions:
* intensity_model(self, csv_file: str [path], pred_dict: dict) -  Loads model, extracts and normalizes input data, makes predictions, and writes to dictionary. Returns dictionary pred_dict.

Class Intensity functions:
* run(tier_name: str, Textgrid_path: str[path], Wav_file_path: str[path]) - Creates Sound object, does calculations on data, and exports the resulting dict. Calls FileProcessorIntensity.IterateTextGridforIntensity, all SpeakerNormalization except getZScore, IntensityFormatToInterval.dictToArr, all IntensityFormatting, all context, all POS, all Saved_Model functions.

#### Clean_P_Model

Requires: parselmouth, tgt, numpy, csv, spacy, pandas, re, os, tensorflow.keras.models, sklearn.preprocessing, datetime

Description: Defines and runs a number of functions related to pitch measures. 

Class PitchExtraction functions:
N.B. an important intermediate data structure is the [parselmouth.Pitch object](https://parselmouth.readthedocs.io/en/latest/api/parselmouth.Pitch.html#parselmouth.Pitch).
* getMaxPitch(self, Wav_file: parselmouth.Sound object, start_time: float, end_time: float) - Returns maximum pitch of a file.
* getMinPitch(self, Wav_file: parselmouth.Sound object, start_time: float, end_time: float) - Returns minimum pitch of a file.
* getPitchStandardDeviation(self, Wav_file: parselmouth.Sound object, start_time: float, end_time: float) - Returns standard deviation of pitch of a file.
* getAveragePitch(self, Wav_file: parselmouth.Sound object, start_time: float, end_time: float) - Returns arithmetic mean of pitch of an interval.

Class SpeakerNormalization functions:
N.B. For all of the below functions: interval_data is a dict mapping strings to arrays. arr is a string representing the dict key to select the array.
* fileMean(self, interval_data: dict, arr: str) - Takes arr and returns the average of the values
* fileStd(self, interval_data: dict, avg: float, arr: str) - Takes arr and average and returns Standard Deviation (Std) of the values
* fileMin(self, interval_data: dict, arr: str) - Takes arr and returns the minimum value
* fileMax(self, interval_data: dict, arr: str) - Takes arr and returns the maximum value
* zScoreAppend(self, interval_data: dict, avg: float, std: float, arr: str) - Takes arr, average, standard deviation and returns the dict with Z-score appended.
* getZScore(self, key: number, avg: float, std: float) - Takes a specific value and returns the Z-score.

Class FileProcessor functions:
* __init__(self) - Runs model by itself calling PitchExtraction()
* iterateTextGridforPitch(self, TextGrid_path: str, tier_name: str, Wav_file: parselmouth.Sound object) - Creates array Interval_data, iterates through intervals of specified TextGrid tier, and runs calculations. Returns array interval_data, int error_count, and array error_arr. Calls all PitchExtraction methods.
  
Class FormatToInterval functions:
* dictToArr(self, arr: dict) - Converts dictionary to array.
* outputArr(self, arr: array) - Prints array.

Class Formatting functions:
* to_csv(self, data: array, csv_file: str [path]) - Creates CSV file out of array and saves it. No returns.

Class Context functions:
* contextWindow(self, complete_data: dictionary) - allows for only local context as opposed to the total context that the speaker normalization class would gather. 

Class POS functions:
* add_pos_column_with_pandas(self, input_csv: str [path], text_column_name: str="Text", new_column_name: str="POS ID's") - Generates POS tags from spaCy model and saves to provided CSV file.
* clean_column(self, input_csv: str [path]) - Keeps only the first number from part of speech IDs.
* extract_first_number(cell) - defined inside clean_column

Class Saved_Model functions:
* pitch_model(self, csv_file: str [path], pred_dict: dict) -  Loads model, extracts and normalizes input data, makes predictions, and writes to dictionary. Returns dictionary pred_dict.

Class Pitch functions:
* run(tier_name: str, Textgrid_path: str[path], Wav_file_path: str[path]) - Creates Sound object, does calculations on data, and exports the resulting dict. Calls FileProcessor.IterateTextGridforPitch, all SpeakerNormalization except getZScore, FormatToInterval.dictToArr, all Formatting, all plswrk, all POS, all Saved_Model functions.

#### Utilities

Requires: praatio, re, tgt

Description: Contains the functions doing the heavy lifting. Merges dictionaries, creates textgrid with tiers, populates. 

Class model_join functions:
* static dict_merge(p_dict: dict, i_dict: dict) - Merges pitch and intensity dictionaries.

Class CTG functions:
* create_textgrid(final_dict: dict, output_file: str [path], reference_textgrid: textgrid.Textgrid object) - Creates a TextGrid object with text, prominence, and boundary tiers. Populates with information from final_dict.
* create_point_tier(final_dict: dict, textgrid_path: str [path], phone_data: str) - Creates point tier in provided textgrid and adds prosody markings according to final_dict. Calls point_tier_setup.

Class Point_Tier functions:
* static phone_data(Textgrid_path: str[path], phone_tier: str) - Creates dictionary from textgrid interval data
* static point_tier_setup(start_time: float, end_time: float, phone_dict: dict, type: string literal ['Prominence', 'Boundary']) - Returns float point_time.
