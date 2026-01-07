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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import Clean_I_Model
import Clean_P_Model
import Utilities
from Utilities import *
from Clean_P_Model import Pitch
from Clean_I_Model import Intensity
import sliceUtterances

class SpeakerFile:
    def __init__(self, wav_filepath, textgrid_filepath):
        def case_manual_format():
            print("\nThis file name or tier name does not match a recognized format. Enter tiers manually.")                      
            word_tier, phone_tier = select_tiers(all_tiers)
            return ("unknown", "unknown", "unknown", word_tier,
                    phone_tier, "unknown", "unknown")

        format_recognized = True #true until proven false

        #derive name variables
        self.wav_filepath = wav_filepath
        self.textgrid_filepath = textgrid_filepath
        self.wav_filename = os.path.basename(wav_filepath)
        self.textgrid_filename = os.path.basename(textgrid_filepath)
        self.name_with_channel = self.wav_filename[0:-4]
        ending = self.name_with_channel.split('_')[-1]
        if not ending:
            print("This file name implies a stereo file. In future please use a single-channel file \
                      \nwith a file name ending in 1 or l for left channel, or 2 or r for right channel. \
                      \nProgram will continue, but recommend you abort if stereo file.")
            self.channel = "unknown"
            format_recognized = False
        else:
            n = len(ending)+1
            self.base_filename = self.name_with_channel[0:-n]

            #derive channel
            last_char = ending[-1].lower()
            if (last_char == '1' or last_char =='l'): #'one' or 'L'
                self.channel = "left"
            elif (last_char == '2' or last_char == 'r'):
                self.channel = "right"
            else:
                print("This file name implies a stereo file. In future please use a single-channel file \
                          \nwith a file name ending in 1 or l for left channel, or 2 or r for right channel. \
                          \nProgram will continue, but recommend you abort if stereo file.")
                self.channel = "unknown"
                format_recognized = False
            
        #summon Sound and TextGrid files from packages    
        self.wav_file_obj = parselmouth.Sound(wav_filepath)
        self.textgrid_obj = tgt.io.read_textgrid(textgrid_filepath)
        
        all_tiers = [t.name for t in self.textgrid_obj.tiers]
        
        #fetch variables found in file naming convention
        if self.name_with_channel[0:4]==("1213"):
            sID, g, word_tier, phone_tier, pn, v = self.MMT1(self.name_with_channel)          
        elif self.name_with_channel[0:4]==("3000"):
            sID, g, word_tier, phone_tier, pn, v = self.MMT2(self.name_with_channel)            
        else:
            format_recognized = False                       
        if word_tier not in all_tiers or phone_tier not in all_tiers or not format_recognized:
                sID, g, word_tier, phone_tier, pn, v = case_manual_format()

        #unpack output
        self.pairing_number = pn
        self.speakerID = sID
        self.word_tier = word_tier
        self.phone_tier = phone_tier
        if g==("f"):
            self.gender = "female"
        elif g==("m"):
            self.gender = "male"
        elif g==("q") or g==("x"):
            self.gender=("nonbinary")
        else:
            self.gender = g
        if v==("aa") or v==("a"):
            self.variety = "African-American"
        elif v==("l"):
            self.variety= "Latine"
        elif v==("m"):
            self.variety = "mainstream"
        else:
            self.variety = v        
        
    def MMT1(self, filename):
        if self.channel == "left":
            speakerID = filename[9:13]
            gender = filename[7]
        elif self.channel == "right":
            speakerID = filename[13:17]
            gender = filename[8]
        else:
            print("Cannot derive speaker ID or gender while channel is not defined.")
            speakerID = "unknown"
            gender = "unknown"
        word_tier = speakerID +(' - words')
        phone_tier = speakerID +(' - phones')
        pairing_number = filename[5:7]
        return speakerID, gender, word_tier, phone_tier, pairing_number, "unknown"

    def MMT2(self, filename):
        info = filename.split('-')
        print(info)
        variety = info[2]
        pairing_number = filename[6:8]
        if self.channel == "left":
            speakerID = pairing_number + '-L'            
            gender = info[3][0]
        elif self.channel == "right":
            speakerID = pairing_number + '-R'
            gender = info[3][1]
        else:
            print("Cannot derive speaker ID or gender while channel is not defined.")
            speakerID = "unknown"
            gender = "unknown"
        word_tier = speakerID[-1]+' - words'
        phone_tier = speakerID[-1]+' - phones'                
        return speakerID, gender, word_tier, phone_tier, pairing_number, variety

    def __repr__(self):
        return(
            "grant number: " + self.base_filename[0:4] + '\n' +
            "wav file path: " + self.wav_filepath + '\n' +
            "textgrid file path: " + self.textgrid_filepath + '\n' +
            "name of .wav file: " + self.wav_filename + '\n' +
            "name of .textgrid file: " + self.textgrid_filename + '\n' +
            "name with channel but without file extension: " + self.name_with_channel + '\n' +
            "name with no channel or file extension: " + self.base_filename + '\n' +
            "textgrid word tier: " + self.word_tier + '\n' +
            "textgrid phone tier: " + self.phone_tier + '\n' +
            "channel: " + self.channel + '\n' +
            "experiment pairing: " + self.pairing_number + '\n' +
            "speaker ID: " + self.speakerID + '\n' +
            "gender: " + self.gender + '\n' +
            "variety: " + self.variety)
          
    def __str__(self):
        return self.name_with_channel
    

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
    
    wav_file_path = filedialog.askopenfilename(title="Select WAV File", filetypes=[("WAV files", "*.wav")])
    if not wav_file_path:
        print("No WAV file selected. Exiting.")
        quit()
        return None, None, None
    
    filename = wav_file_path.split('/')[-1]
    filename_stripped = filename[0:-6]
    textgrid_path = os.path.join(gen_textgrid_path,(filename_stripped + ".TextGrid"))
    speaker_file = SpeakerFile(wav_file_path, textgrid_path)
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
    print(repr(s))
    pred_textgrid_name = s.name_with_channel + "_Predictions.TextGrid"
    
    #prep save environment
    #print(save_path)
    if not save_path:
        current_path = os.getcwd()
        save_path = current_path
    #print(save_path)
    tg_output_path=os.path.join(save_path, "TextGrid_output")
    csv_path = os.path.join(save_path, "CSV_output")                                
    #print("tg_output_path =",tg_output_path)
    if not os.path.exists(tg_output_path):
        os.makedirs(tg_output_path)
    #print("csv_path =",csv_path)
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
        print("Splitting utterances...")
        sliced_save_path = os.path.join(save_path, "sliced-utterance-output", s.variety)
        sliceUtterances.just_one_moneypenney(s.wav_filepath, s.textgrid_filepath,
                                             sliced_save_path, pred_dict,
                                             s.word_tier, s.phone_tier)

    print("Operation complete.")

if __name__ == "__main__":
    """
    Only one of these two should be uncommented at a time. See descriptions of methods to pick one.
    """
    #speaker_file = select_files()
    speaker_file, save_path = pull_files_from_path()

    """Only one of these two should be uncommented at a time."""
    if speaker_file: main(speaker_file, save_path=save_path)
    #batch_process()
