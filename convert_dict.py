class Utterance:
    end = 1000000000
    transcript = ""
    
    def __init__(self, position, filename, speaker, start):
        self.position = position
        self.filename = filename
        self.speaker = speaker
        self.start = start

    def __repr__(self):
        return f"{self.speaker} utterance #{self.position} ({round(self.start,4)}-{round(self.end,4)}): {self.transcript} from {self.filename}"

from pprint import pprint
def process_utterances(d, filename, speaker):
    """
    Splits a final_dictionary from autorpt or open_csv into utterance-long segments.
    Args: dictionary d, string filename, string speaker
    Returns: list of Utterance objects objs, dictionary file_transcript
    """
    #print("begin process_utterances")
    d_intervals = d["Interval"]
    d_text = d["Text"]
    d_starts = d["start"]
    d_ends = d["end"]
    d_next_starts = d["next_start"]

    objs = []

    file_transcript = {}
    reset = True
    utt_num = 0

    for j in range(0, len(d_intervals)):
        text = d_text[j]       
        if text != "[bracketed]":
      
            if reset == True:
                file_transcript.update({utt_num:[]})
                spaced_start = max(d_starts[j]-0.0001,0)
                i = Utterance(utt_num, filename, speaker, spaced_start)
                h = ""
            
            h+=(text)
            h+=(" ")
            try:
                file_transcript[utt_num].append(text)
            except KeyError:
                file_transcript.update({utt_num:[]})
                file_transcript[utt_num].append(text)
                file_transcript[utt_num].append("KeyError thrown; created entry")
                print("KeyError thrown; created entry; check file transcript")
        # This is where the utterance boundary size is determined
        is_boundary = d_next_starts[j] - d_ends[j] > 1
        if is_boundary:
            spaced_end = min(d_ends[j]+0.0001, d_ends[-1])
            i.end = spaced_end
            i.transcript = h
            utt_num += 1
            objs.append(i)
            reset = True
        else:
            reset = False
        j += 1
##    pprint(file_transcript)
    #print('\n',"objs")
    #pprint(objs)
    #print("end process_utterances")
    return objs, file_transcript

import csv
import tkinter as tk
from tkinter import filedialog
from sliceUtterances import *

def open_csv():
    """
    Opens a csv and splits it into arrays for process_utterances.
    Args: none
    Returns: process_utterances(intervals, texts, starts, ends, next_starts)
    """
    d = {
    "Interval": [],
    "Text": [],
    "start": [],
    "end": [],
    "next_start": []
    }
    filepath = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            d["Interval"].append(int(row[0]))
            d["Text"].append(row[1])
            d["start"].append(float(row[9]))
            d["end"].append(float(row[10]))
            d["next_start"].append(float(row[11]))
    #print("open_csv:",d)
    return (d)


