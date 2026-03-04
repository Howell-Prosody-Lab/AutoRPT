#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import tgt
import parselmouth
import traceback
import tkinter as tk
from tkinter import filedialog
from praatio import textgrid

#Add the current directory to sys.path
import sys
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#import .Clean_I_Model
#import .Clean_P_Model
#import .Utilities
#import .SpeakerFile
from .SpeakerFile import *
from .Utilities import *
from .Clean_P_Model import Pitch
from .Clean_I_Model import Intensity
    

def select_tiers(all_tiers):
    # Allows user to enter tier names manually. Used when file naming convention not recognized.
    # Args: list of strings all_tiers
    # Returns: string word_tier, string phone_tier
    root = tk.Tk()
    root.withdraw()
    print("Available tiers include:")
    print(all_tiers)
    continue_prog = False
    while not continue_prog:
        word_tier = input("Enter the word tier name in the TextGrid: ")
        if word_tier in all_tiers:
            continue_prog = True
        elif word_tier.lower() in ["cancel","quit","exit"]:
            print("Exiting.")
            quit()
        else:
            print("Not a valid tier.")
    continue_prog = False
    while not continue_prog:
        phone_tier = input("Enter the phone tier name in the TextGrid: ")
        if phone_tier in all_tiers:
            continue_prog = True
        elif phone_tier.lower() in ["cancel","quit","exit"]:
            print("Exiting.")
            quit()
        else:
            print("Not a valid tier.")
    return word_tier, phone_tier

def select_files():
    """
    Opens a file dialog to select TextGrid and WAV files.
    Args: none
    Returns: SpeakerFile object speaker_file
    """
    root = tk.Tk()
    root.withdraw() 

    print("Choose a TextGrid file from the file dialog.")
    textgrid_path = filedialog.askopenfilename(title="Select TextGrid File", filetypes=[("TextGrid files", "*.TextGrid")])
    if not textgrid_path:
        print("No TextGrid file selected. Exiting.")
        quit()
        return None, None, None

    print("Choose a WAV file from the file dialog.") 
    wav_file_path = filedialog.askopenfilename(title="Select WAV File", filetypes=[("WAV files", "*.wav")])
    if not wav_file_path:
        print("No WAV file selected. Exiting.")
        quit()
        return None, None, None

    speaker_file = SpeakerFile(wav_file_path, textgrid_path)
  
    return speaker_file


def pull_files_from_path():
    # Selects source files directly from filepath
    # Args: None
    # Returns: SpeakerFile object speaker_file, path-like string gen_save_path
    
    root = tk.Tk()
    root.withdraw()

    f = open("pull_files_from_path.txt")
    gen_textgrid_path = f.readline()[0:-1]
    gen_wav_path = f.readline()[0:-1]
    gen_save_path = f.readline()[0:-1]
    print("WAV files:",gen_wav_path)
    print("TextGrids:",gen_textgrid_path)
    print("Saved files in:",gen_save_path)
    f.close()
    
    wav_file_path = filedialog.askopenfilename(title="Select WAV File", filetypes=[("WAV files", "*.wav")], initialdir=gen_wav_path)
    if not wav_file_path:
        print("No WAV file selected. Exiting.")
        quit()
        return None, None, None
    
    speaker_file = SpeakerFile(wav_file_path = wav_file_path)
    filename = wav_file_path.split('/')[-1]
    filename_stripped = filename[0:filename.rfind('_')]
    textgrid_path = os.path.join(gen_textgrid_path,(speaker_file.base_filename + ".TextGrid"))
    speaker_file.add_textgrid(textgrid_path)
    #print (textgrid_path)
    return speaker_file, gen_save_path

def batch_process():
    # Runs main on whole folder of files using the same logic as pull_files_from_path().
    # Args: None
    # Returns: None
    root = tk.Tk()
    root.withdraw()

    f = open("pull_files_from_path.txt")
    gen_textgrid_path = f.readline()[0:-1]
    gen_wav_path = f.readline()[0:-1]
    gen_save_path = f.readline()[0:-1]
    print(gen_textgrid_path)
    print(gen_save_path)
    f.close()
    print("\nYou said you keep your textgrid files here: ", gen_textgrid_path)
    print("And your WAV files here: ", gen_wav_path)
    continue_prog = input("If that isn't right, please update pull_files_from_path.txt and restart this program. Continue? (Y/N)")
    if (continue_prog not in ['Y', 'y', "yes", "Yes", "correct"]):
        print("Exiting.")
        quit()
        return None, None, None
    skipped_files = ""
    for filename in os.listdir(gen_wav_path):
        name_with_channel = filename[0:-4]
        ending = name_with_channel.split('_')[-1]
        if not ending:
            print("To use batch process, file names must be predictable. All .wav files \
                  \nmust end in _1 (or _ch1) for left and _2 (or _ch2) for right. All .TextGrid files \
                  must have the same name minus the _1 or equivalent.")
            quit()
        else:
            n = len(ending)+1
            base_filename = name_with_channel[0:-n]
            print(f"filename = {filename}, name_with_channel = {name_with_channel}, base_filename = {base_filename}")
        wav_file_path = os.path.join(gen_wav_path, filename)
        textgrid_path = os.path.join(gen_textgrid_path,(base_filename + ".TextGrid"))
        
        print('\n')       
        try:
            speaker_file = SpeakerFile(wav_file_path, textgrid_path)
            main(speaker_file, gen_save_path, split_utterances=False)
        except (TypeError, FileNotFoundError):
            skipped_files += (wav_file_path, '\n', traceback.format_list(traceback.extract_stack()), '\n')
            continue
    if skipped_files != "":
        print("Skipped files: \n", skipped_files)
    print("Batch complete")
    
def main(s, save_path = None, split_utterances=False):
    # Gets provided metadata from one of the data select functions and runs pitch and intensity functions.
    # Args: SpeakerFile s
    # Kwargs: path-like string save_path, boolean split_utterances
    # Returns: none
    print(repr(s),'\n')
    if not s.has_textgrid() or not s.has_wav():
        print(f"Textgrid? {s.has_textgrid()} WAV file? {s.has_wav()} Without both files the operation cannot continue. Exiting.")
        quit(1)
    pred_textgrid_name = s.name_with_channel + "_Predictions.TextGrid"
    
    #prep save environment
    if not save_path:
        current_path = os.getcwd()
        save_path = current_path
    tg_output_path=os.path.join(save_path, "TextGrid_output")
    csv_path = os.path.join(save_path, "CSV_output")                                
    if not os.path.exists(tg_output_path):
        os.makedirs(tg_output_path)
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
        
    tg_output_file = os.path.join(tg_output_path, pred_textgrid_name)

    try:
        pitch_dict = Pitch.run(s, csv_path)
        intensity_dict = Intensity.run(s, csv_path)
    except:
        print(traceback.format_exc())
        quit()
    print("Joining model...")
    pred_dict = model_join.dict_merge(pitch_dict, intensity_dict)

    print("Creating textgrid...")
    CTG.create_textgrid(pred_dict, tg_output_file, s.textgrid_filepath)
    phone_dict = Point_Tier.phone_data(s.textgrid_filepath, s.phone_tier)
    CTG.create_point_tier(pred_dict, tg_output_file, phone_dict)
   
    print("Creating and outputting final_dict...")
    printable = mdictToArr(pred_dict)
    filepath=os.path.join(csv_path,s.name_with_channel+"_final.csv")
    mto_csv(data=printable,csv_file=filepath)

    if split_utterances:
        import sliceUtterances
        print("Splitting utterances...")
        sliced_save_path = os.path.join(save_path, "sliced-utterance-output", s.variety)
        sliceUtterances.just_one_moneypenney(s.wav_filepath, s.textgrid_filepath,
                                             sliced_save_path, pred_dict,
                                             s.word_tier, s.phone_tier)

    print("Operation complete.")

def cli():
    save_path = None

    if "--help" in sys.argv:
        print('''
Usage: autorpt <wav> <textgrid> <word_tier> [<phone_tier>]

Additional Flags:
    --batch (for batch processing of multiple files)
    --select (for manually selecting files/tiers with a file selector)

You may also make a file 'pull_files_from_path.txt'. Running autorpt in the same directory as this file will pull arguments from this file instead of the command line.
                ''')
        return

    if "--select" in sys.argv:
        speaker_file = select_files()

    elif "--batch" in sys.argv:
        # usage: LSTM_RPT.py --batch
        # see batch_process() method for more details
        batch_process()
        return

    else:
        pos_args = [a for a in sys.argv[1:] if not a.startswith('--')]
        if len(pos_args) >= 3:
            wav_path, tg_path, word_tier = pos_args[0], pos_args[1], pos_args[2]
            phone_tier = pos_args[3] if len(pos_args) >= 4 else None
            speaker_file = SpeakerFile(wav_file_path=wav_path, textgrid_file_path=tg_path,
                                       word_tier=word_tier, phone_tier=phone_tier)
        elif os.path.exists("pull_files_from_path.txt"):
            speaker_file, save_path = pull_files_from_path()
        else:
            speaker_file = select_files()

    if speaker_file: main(speaker_file, save_path=save_path, split_utterances=True)

if __name__ == "__main__":
    cli()
