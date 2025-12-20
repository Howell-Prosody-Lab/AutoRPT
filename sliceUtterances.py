import glob
import os
import subprocess
import sys
import textgrid
import traceback
import logging
import datetime
import bisect
from convert_dict import *

# Logger setup
# Logger.debug lines work like print statements, except you can turn them all
# on or off with one line change.
logger = logging.getLogger(__name__)
error_filename = 'error_log_' + str(datetime.datetime.today()).replace(':', '_') + '.log'
debug_level = logging.DEBUG # bit in all caps can be ERROR (for normal operation), INFO or DEBUG (activity log created)
logging.basicConfig(filename=error_filename, encoding='utf-8', level=debug_level)
logger.info(os.getcwd())

def binary_search_min(a, x):
    #Find rightmost value less than x
    # list a, double x -> int
    i = bisect.bisect_left(a, x, key=(lambda r: r.minTime))
    if i:
        return i-1
    raise ValueError

def binary_search_max(a, x):
    #Find leftmost value greater than x
    # list a, double x -> int
    i = bisect.bisect_right(a, x, key=(lambda r: r.maxTime))
    if i != len(a):
        return i
    raise ValueError

def sliceTg(tg, start, end, tier_names, interval_lists):
  """
  # Copies all relevant slices of textgrid into fresh ones.
  # Args: textgrid.TextGrid item tg, timestamp str start, timestamp str end,
  # tuple tiers (contains names of phone-tier and word-tier), list of lists of intervals interval_lists
  # Returns: textgrid.TextGrid item nu_tg
  """
  logger.debug(f"start sliceTg: tg={tg}\nstart={start},\nend={end},\ntier_names={tier_names}\n")
  #creating blank textgrid
  nu_tg = textgrid.TextGrid()
  for tier_name, tier in zip(tier_names, interval_lists):
    #add only relevant tiers to new textgrid
    nu_tg.append(textgrid.IntervalTier(name=tier_name))
    #select only the intervals in the right area for evaluation
    range_min = binary_search_min(tier, start)
    range_max = binary_search_max(tier, end)
    logger.debug(f"Tier {tier_name} range = {range_min}-{range_max}")
    for j in range(range_min, range_max): #for each of those intervals:
      interval = tier[j]
      orig_mintime = interval.minTime
      orig_maxtime = interval.maxTime
      new_mark = interval.mark
      logger.debug(f"{j} interval {interval} retrieved as ({orig_mintime}, {orig_maxtime}, {new_mark})")
      if ((orig_mintime >= start) and (orig_maxtime <= end)):
        logger.debug(f"###interval is gte start & lte end")
        # copy intervals with modified times
        new_mintime = round(max(0, orig_mintime - start), 7)
        new_maxtime = round(orig_maxtime - start, 7)          
        try:
          nu_tg_tier=nu_tg.getFirst(tier_name)
          logger.info(f"  new TextGrid tier called: {nu_tg_tier}")
          nu_tg_tier.add(new_mintime, new_maxtime, new_mark)
          logger.debug(f"  now we have:{repr(nu_tg_tier)}\n")
        except:
          print(f"tier_name={tier_name}, time={new_mintime}-{new_maxtime}")
          print(traceback.format_exc())
          quit()

  for t in nu_tg.tiers:
    logger.info(f"{t} exists? {not not t}")
    if not t:
      logger.debug(f"{t} is still empty, see original at {start}-{end}")
  logger.info("end sliceTg\n")
  return nu_tg
        

def sliceAudio(audiofile, start, end, output):
  """
  # Slices sections of audio based on provided timestamps.
  # Args: path-like string audiofile, timestamp string start, timestamp
  #   str end, path-like string output
  # Returns: none. Outputs .wav files.
  """
  length = end-start
  if os.path.isfile(output):
    os.remove(output)
    
  command = [
      'ffmpeg',
      '-i', audiofile,
      '-ss', str(start),  
      '-t', str(length),
      output           # Output
  ]

  subprocess.run(command, check=True)
  
def pad(i, length):
    #takes a number as a string and sees if it has enough leading zeros to be sortable
    # str i, int length -> str i
    current = len(i)
    if current < length:
        return pad(('0'+i), length)
    else:
        return i

def just_one_moneypenney(audiofile, tg_file_path, save_path, d, word_tier, phone_tier):
  """
  # Runs on a single file instead of a folder full of them, allows for
  # integration into autorpt. Splits a wav file into its component utterances
  # and transcript by pulling from its combined csv file.
  # Args: path-like string audiofile, path-like string tg_file_path,
  #   path-like string save_file_gen_path, dictionary d, string word_tier,
  #   string phone_tier.
  # Returns: none. Outputs a folder of audio, textgrid, and txt files.
  """
  logger.info("begin just_one_moneypenney")
  tg = textgrid.TextGrid.fromFile(tg_file_path)
  logger.debug(f"files: {tg}, {audiofile}")
  file_name = os.path.basename(audiofile)[:-4] 
  file_dir = os.path.join(save_path, file_name)
  speaker_Id = word_tier[0:4]
  logger.debug(f"{file_name} {file_dir}")
  if not os.path.exists(file_dir):
    os.makedirs(file_dir)
  os.chdir(file_dir)

  logger.info("calling process_utterances...")
  #data is a list of Utterance objects, transcript is a dictionary 
  data, transcript = convert_dict.process_utterances(d, file_name, speaker_Id) 
  #pprint(transcript)
  
  logger.info("setting up file for transcript...")
  f = open(f"{file_name}.txt", "w")   
  length = len(data)
  tiers = (word_tier, phone_tier)
  interval_lists = []
  logger.info("adding tiers...")
  for i in range(0, len(tg)):
    source_tier_name = tg[i].name
    if source_tier_name in tiers: 
      logger.info(f"{source_tier_name}, adding")
      interval_lists.append(tg[i].intervals)

  logger.info("preparing to iterate through data list...")  
  for i in range(length):
    sortable_i = pad(str(i), len(str(length)))
    utterance_name = file_name + f"_utt{sortable_i}"
    tg_out = os.path.join(file_dir,(utterance_name + ".TextGrid"))
    au_out = os.path.join(file_dir,(utterance_name + ".wav"))
    logger.debug(f"calling sliceTg on utterance {i} with {data[i].start}, {data[i].end}...")
    sliced_text_object = sliceTg(tg, data[i].start, data[i].end, tiers, interval_lists)
    logger.debug(f"loop #{i}/{length}, sliced_text_object:{sliced_text_object}")
    logger.debug(f"tiers[0] maxTime={tg[0].maxTime}, tiers[1] maxTime={tg[1].maxTime}")
    logger.info("beginning textgrid write...")
    sliced_text_object.write(tg_out)
    logger.info("beginning sliceAudio...")
    sliceAudio(audiofile, data[i].start, data[i].end, au_out)
    logger.debug("beginning mini transcript write...")
    g = open(f"{utterance_name}.txt", "w")
    g.write(data[i].transcript)
    g.close()
    logger.debug("beginning major transcript write")
    try:
        f.write(f'{i}\n')
        logger.debug(f"i={i}")
        logger.debug(f"transcript[i] = {transcript[i]}")
        logger.debug(f"len(transcript[i] = {len(transcript[i])}")
        for j in range(len(transcript[i])):
          f.write(transcript[i][j])
          f.write(' ')
        f.write('\n')
    except KeyError:
        continue #an interval that doesn't have an entry (like a speech sound)
    
  f.close()
  logger.debug("end just_one_moneypenney")                        
    
def main():
  # Not done yet. Intending to add functionality to pull the csv and convert to
  # dictionary.
  f = open("slicy.txt")
  txt_file_path = f.readline()[0:-1]
  wav_file_path = f.readline()[0:-1]
  save_path = f.readline()[0:-1]
  start = float(f.readline()[0:-1])
  end = float(f.readline()[0:-1])

  # load files
  textgrids = glob.glob(txt_file_path + "/*TextGrid")
  print("length of textgrids =", len(textgrids))
  audio = glob.glob(wav_file_path + "/*wav")
  logger.debug("length of audio =", len(audio))
  for i in range(0,len(audio)):
    audiofile = audio[i]
    tg = textgrid.TextGrid.fromFile(wav_file_path + "/" + os.path.basename(audio[i])[:-6] + '.TextGrid')
    logger.debug("file:")
    logger.debug(tg)
    logger.debug(audiofile)

    tg_out = os.path.join(save_path,audio[i])[:-4] + f"_int{i}.TextGrid"
    logger.debug("tg_out:",tg_out)

    au_out = os.path.basename(audio[i])[:-4] + f"_int{i}.wav"

  # gaming
  sliced_text_object = sliceTg(tg, start, end)
  sliced_text_object.write(tg_out)
  sliceAudio(audiofile, start, end, au_out)

import convert_dict
import os

def test(file):
  #allows us to test this module without running rpt
  f = open("pull_files_from_path.txt")
  gen_textgrid_path = f.readline()[0:-1]
  gen_wav_path = f.readline()[0:-1]
  save_file_gen_path = f.readline()[0:-1]
  f.close()
  if file==1:
    tg_file_path = os.path.join(gen_textgrid_path, "1213p48mx92zr82pv.TextGrid")
    wav_file_path = os.path.join(gen_wav_path, "1213p48mx92zr82pv_1.wav")
    word_tier = "92zr - words"
    phone_tier = "92zr - phones"
  elif file==2:
    tg_file_path = os.path.join(gen_textgrid_path, "1213p02fm02kw09rl.TextGrid")
    wav_file_path = os.path.join(gen_wav_path, "1213p02fm02kw09rl_2.wav")
    word_tier = "09rl - words"
    phone_tier = "09rl - phones"
  elif file==3:
    tg_file_path = os.path.join(gen_textgrid_path, "3000-p06-l-ff.TextGrid") 
    wav_file_path = os.path.join(gen_wav_path, "3000-p06-l-ff_ch1.wav")
    word_tier = "L - words"
    phone_tier = "L - phones"
  d = convert_dict.open_csv()
  just_one_moneypenney(wav_file_path, tg_file_path, save_file_gen_path, d, word_tier, phone_tier)
  print("test complete")

 
if __name__ == "__main__":
    test(3)
