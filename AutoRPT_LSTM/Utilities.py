#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import traceback
import csv

def mto_csv(data, csv_file):
        # Creates CSV file out of array and saves it.
        # Args: data: array, csv_file: str [path]. Returns: none
        
        # Specify the CSV file name
        csv_directory = os.path.dirname(csv_file)
        if not os.path.exists(csv_directory):
            os.makedirs(csv_directory)      
        
        # Write the sub-arrays to the CSV file
        with open(csv_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
    
            # Iterate through the sub-arrays and write each element in separate columns
            for sub_array in data:
                 csv_writer.writerow(sub_array)

        print(f'Data has been written to {csv_file}.')

        
def mdictToArr(d):
    # Converts dictionary to array.
    # Args- d: dict
    # Returns array arr.

    # Initialize first array with formatting
    arr = []
    ordered_keys = [k for k in d.keys()]
    #print(d.keys())
    #print(ordered_keys)
    formatter = {"STD": "Standard Deviation", "Std": "Standard Deviation", "Z-SCORE": "Z-Score", "dur": "Duration"}
    # header = x from columns but in title case unless x is in formatter, then use value from formatter
    header = [x.title() if x not in formatter.keys() else formatter[x] for x in ordered_keys]
    #print(header)
    arr.append(header)
    
    # Create User-Output Array
    # for every number in range of d, row=d[column][number]
    for i in range(len(d["Interval"])):
        arr.append([])
    for k in ordered_keys:
        j=1
        for v in d[k]:
            arr[j].append(v)
            j+=1
    return arr

def moutputArr(arr):
    # Prints array.
    # Args: arr: array   
    for i, array in enumerate(arr):
        print(array)

import numpy as np
class model_join:
    
    @staticmethod
    def dict_merge(p_dict, i_dict):
        # Merges pitch and intensity dictionaries.
        # Args: p_dict: dict, i_dict: dict. Returns: final_dict dict
        
        p_intervals = p_dict["Interval"]
        i_intervals = i_dict["Interval"]
        p_start = p_dict["start"]
        i_start = i_dict["start"]
        p_end = p_dict["end"]
        i_end = i_dict["end"]
        i_text = i_dict["Text"]
        p_text = p_dict["Text"]

        total_max = max(max(p_intervals), max(i_intervals))
        #print("total_max =",total_max)
        #print(p_intervals)
        #print(i_intervals)
                               
        j = 1
        pitch = 0
        intensity = 0
        
        # Initialize dictionary lists
        final_dict = {
            "Interval": [],            
            "Text": [],
            "Pitch_prominence": [],
            "Intensity_prominence": [],
            "Prominence": [],
            "Pitch_boundary": [],
            "Intensity_boundary": [],
            "Silence_boundary": [],
            "Boundary": [],
            "start": [],
            "end": [],
            "next_start": [],
            "pitch_interval": [],
            "intensity_interval": [],
            "Prominence_label": [],
            "Boundary_label" : []
        }

        while j < total_max:
            if not (j in p_intervals or j in i_intervals):
                j += 1
                continue
            final_dict["Interval"].append(j) #Col A
            final_dict["pitch_interval"].append(pitch) #incrementer used as index
            final_dict["intensity_interval"].append(intensity)
            #print(f'j={j}, pitch={pitch}, intensity={intensity}')
            
            if j>=total_max-1:
                #s_bound = 0.9
                next_start = 100000000 #"infinity"
            else:
                #looking at start of next item
                next_start = min(p_start[pitch+1], i_start[intensity+1])
                
            final_dict["next_start"].append(next_start)   
            
            prom_values = []
            bound_values = []
            

            if j in p_intervals: #if pitch data exists
                #collect text/start/end
                final_dict["Text"].append(p_text[pitch]) #Col B
                final_dict["start"].append(p_start[pitch]) #Col J
                interval_end = p_end[pitch]
                #record pitch values
                p_prom = p_dict["Prominence_raw"][pitch]
                p_bound = p_dict["Boundary_raw"][pitch]
                #round to avoid rounding errors later
                final_dict["Pitch_prominence"].append(round(p_prom,4)) #Col C
                final_dict["Pitch_boundary"].append(round(p_bound, 4)) #Col D
                #pitch candidates to contribute to end values
                prom_values.append(p_prom)
                bound_values.append(p_bound)
                pitch += 1
            else: #if no pitch data
                #placeholders for cols C-D so that next round of data ends up in the correct row
                final_dict["Pitch_prominence"].append('')
                final_dict["Pitch_boundary"].append('')
                #t, we know that if we don't have pitch data
                #we must have intensity data
                #use that for text/start/end
                text = i_text[intensity]
                final_dict["Text"].append(text) #Col B (alt)
                final_dict["start"].append(i_start[intensity]) #Col J (alt)
                interval_end = i_end[intensity]

            if j in i_intervals: #if intensity data exists
                #regardless of p_intervals, collect intensity data
                i_prom = i_dict["Prominence_raw"][intensity] 
                i_bound = i_dict["Boundary_raw"][intensity]
                final_dict["Intensity_prominence"].append(round(i_prom, 4)) #Col F
                final_dict["Intensity_boundary"].append(round(i_bound, 4)) #Col G
                #intensity candidates to contribute to end values
                prom_values.append(i_prom)
                bound_values.append(i_bound)
                intensity += 1
            else: #if no intensity data
                #placeholders for cols G-H so next round of data ends up in correct row
                final_dict["Intensity_prominence"].append('')
                final_dict["Intensity_boundary"].append('')

            if interval_end + 2 < next_start:
                s_bound = 0.9
            else:
                s_bound = 0.3
            final_dict["end"].append(interval_end) #Col K
            final_dict["Silence_boundary"].append(s_bound) #Col H
            #Silence candidate to contribute to final boundary value
            bound_values.append(s_bound)
            
            #final prominence and boundary numbers
            prom = round(np.mean(prom_values), 2)
            bound = round(np.mean(bound_values), 2)              
            final_dict["Prominence"].append(prom) #Col E
            final_dict["Boundary"].append(bound) #Col I

            j += 1  # Always increment j
        #print(final_dict)
        #print("end model_join")
        return final_dict


# In[ ]:


from praatio import textgrid
import re

class CTG:
    
    
    def create_textgrid(final_dict, output_file, reference_textgrid):
        """
        # Creates a TextGrid object with text, prominence, and boundary tiers.
        # Populates with information from final_dict.
        # Args: final_dict: dict, output_file: str [path], reference_textgrid: textgrid.Textgrid object
        # Returns: None
        """
        
        tg = textgrid.Textgrid()
        
        ref_tg = textgrid.openTextgrid(reference_textgrid, includeEmptyIntervals=True)
        max_et = ref_tg.maxTimestamp

        text_tier = textgrid.IntervalTier("Text", [], minT=0, maxT=max_et)
        prominence_tier = textgrid.IntervalTier("Prominence", [], minT=0, maxT= max_et)
        boundary_tier = textgrid.IntervalTier("Boundary", [], minT=0, maxT=max_et)
        
        for start, end, text, prominence, boundary in zip(
            final_dict["start"],
            final_dict["end"],
            final_dict["Text"],
            final_dict["Prominence"],
            final_dict["Boundary"]
        ):
            
            start = float(start)
            end = float(end)
            text = str(text)


            text_tier.insertEntry((start, end, text))
            prominence_tier.insertEntry((start, end, str(prominence)))
            boundary_tier.insertEntry((start, end, str(boundary)))

            
        tg.addTier(text_tier)
        tg.addTier(prominence_tier)
        tg.addTier(boundary_tier)
        
        tg.save(output_file, format="long_textgrid", includeBlankSpaces=True)




    def create_point_tier(final_dict, textgrid_path, phone_data):
        # Creates point tier in provided textgrid and adds prosody markings according to final_dict.
        # Args: final_dict: dict, textgrid_path: str [path], phone_data: str
        # Returns: None
        
        tg = textgrid.openTextgrid(textgrid_path, includeEmptyIntervals=True)
        tier = next((t for t in tg.tiers if t.name == "Text"), None)

        if tier is None:
            print("Text tier not found")
            return
        
        intervals = tier.entries
        if not intervals:
            print("No intervals in tier")
            return
        
        
        min_t = intervals[0].start
        max_t = intervals[-1].end

        time_stamps = {}

        for idx, element in enumerate(final_dict["Prominence"]):
            if 0.41 <= element <= 0.7:
                point = Point_Tier.point_tier_setup(final_dict["start"][idx], final_dict["end"][idx], phone_data, "Prominence")
                time_stamps[point] = "*?"

            elif 0.71 <= element <= 1:
                point = Point_Tier.point_tier_setup(final_dict["start"][idx], final_dict["end"][idx], phone_data, "Prominence")
                time_stamps[point] = "*"

        for idx, element in enumerate(final_dict["Boundary"]):
            if 0.16 <= element <= 0.29:
                point = Point_Tier.point_tier_setup(final_dict["start"][idx], final_dict["end"][idx], phone_data, "Boundary")
                time_stamps[point] = "]?"

            elif 0.3 <= element <= 1:
                point = Point_Tier.point_tier_setup(final_dict["start"][idx], final_dict["end"][idx], phone_data, "Boundary")
                time_stamps[point] = "]"


        sorted_time_stamps = [(k, time_stamps[k]) for k in sorted(time_stamps)]

        point_tier = textgrid.PointTier("RPT", sorted_time_stamps, minT=min_t, maxT = max_t)


        if phone_data["Start"] and phone_data["End"]:
            phone_tier = textgrid.IntervalTier("phone", [], minT=min_t, maxT= max_t)

            for start, end, text in zip(phone_data["Start"], phone_data["End"], phone_data["Text"]):
                phone_tier.insertEntry((float(start), float(end), str(text)))

        else:
            print("Phone tier is empty")

        tg.addTier(phone_tier)
        tg.addTier(point_tier)
        tg.save(textgrid_path, format="long_textgrid", includeBlankSpaces=True)

                
        

from praatio import textgrid   
import re     
import tgt


class Point_Tier:

    import re
    
    @staticmethod
    def phone_data(Textgrid_path, phone_tier):
        # Creates dictionary from textgrid interval data
        # Args: Textgrid_path: str[path], phone_tier: str
        # Returns: dict interval_dict
       
    # Load the TextGrid file using `tgt`
        tgt_text_grid = tgt.io.read_textgrid(Textgrid_path)

    # Find the specified tier
        tier = next((t for t in tgt_text_grid.tiers if t.name == phone_tier), None)

        if tier is None:

            return None  # Or raise an error if needed

    # Create the interval dictionary
        interval_dict = {"Start": [], "End": [], "Text": []}

    # Extract data from annotations
        for annotation in tier.annotations:
            interval_dict["Start"].append(annotation.start_time)
            interval_dict["End"].append(annotation.end_time)
            interval_dict["Text"].append(annotation.text)

        return interval_dict  # Returns the same structure as before

    
    @staticmethod
    def point_tier_setup(start_time, end_time, phone_dict, type):
        # Reads interval data from dictionary
        # Args: start_time: float, end_time: float, phone_dict: dict, type: string literal ['Prominence', 'Boundary']
        # Returns: float point_time

        if start_time in phone_dict["Start"]:
            j = phone_dict["Start"].index(start_time)
        else:
            print(f"Warning: start_time {start_time} not found in phone_dict['Start']")
            return None
    
        continue_loop = True
        temp = {"Start": [], "End": [], "Text": []}

        while continue_loop:
            if j >= len(phone_dict["Start"]):  # Ensure j does not go out of range
                break

            pd_start = phone_dict["Start"][j]
            pd_end = phone_dict["End"][j]
            pd_text = phone_dict["Text"][j]

            if pd_start >= start_time and pd_end <= end_time:
                temp["Start"].append(pd_start)
                temp["End"].append(pd_end)
                temp["Text"].append(pd_text)
                j += 1  # Move to the next index
            else:
                continue_loop = False  # Stop looping if outside range

        if not temp["Text"]:
            print(f"Warning: No matching intervals for start_time {start_time}")
            return None  # Or another fallback value

        stress_index = min(
            range(len(temp["Text"])), 
            key=lambda i: 0 if '1' in temp["Text"][i] else float('inf'),
            default = None
        )

        if stress_index is None:
            print(f"Warning: Could not find valid min_index for start_time {start_time}")
            return None

        low_start = temp["Start"][stress_index]
        low_end = temp["End"][stress_index]

        if type == "Prominence":
            point_time = (low_start + low_end) / 2
        else:
            point_time = end_time #Changed to end_time to put ] to match at end of larger interval (words not phones)

        return point_time
