from LSTM_RPT import *
import os

def integration_test1():
    # Quickest way to test the file. Works on a specific set of 2-minute files in a specific file directory.
    # Args: None.
    # Returns: path-like string textgrid_path, path-like string wav_file_path,
    #   string word_tier, string phone-tier, string gen_ save_path
    print("Reading files...")
    f = open("pull_files_from_path.txt")
    gen_textgrid_path = f.readline()[0:-1]
    gen_wav_path = f.readline()[0:-1]
    gen_save_path = f.readline()[0:-1]
    f.close()
    textgrid_path = os.path.join(gen_textgrid_path, "1213p48mx92zr82pv.TextGrid")
    wav_file_path = os.path.join(gen_wav_path, "1213p48mx92zr82pv_1.wav") 
    print(textgrid_path)
    print(wav_file_path)
    speaker_file = SpeakerFile(wav_file_path, textgrid_path)
    return speaker_file, gen_save_path

def integration_test2():
    #same as integration test 1 but with a full length file
    print("Reading files...")
    f = open("pull_files_from_path.txt")
    gen_textgrid_path = f.readline()[0:-1]
    gen_wav_path = f.readline()[0:-1]
    gen_save_path = f.readline()[0:-1]
    f.close()
    textgrid_path = os.path.join(gen_textgrid_path, "1213p02fm02kw09rl.TextGrid")
    wav_file_path = os.path.join(gen_wav_path, "1213p02fm02kw09rl_2.wav") 
    print(f"Textgrid path = {textgrid_path}")
    print(f"WAV file path = {wav_file_path}")
    speaker_file = SpeakerFile(wav_file_path, textgrid_path)
    return speaker_file, gen_save_path

def integration_test3():
    #same as integration test 2 but with an MMT2 file
    print("Reading files...")
    f = open("pull_files_from_path.txt")
    gen_textgrid_path = f.readline()[0:-1]
    gen_wav_path = f.readline()[0:-1]
    gen_save_path = f.readline()[0:-1]
    f.close()
    textgrid_path = os.path.join(gen_textgrid_path, "3000-p06-l-ff.TextGrid")
    wav_file_path = os.path.join(gen_wav_path, "3000-p06-l-ff_ch1.wav") 
    print(f"Textgrid path = {textgrid_path}")
    print(f"WAV file path = {wav_file_path}")
    speaker_file = SpeakerFile(wav_file_path, textgrid_path)
    return speaker_file, gen_save_path

if __name__ == "__main__":
    """
    Only one of these three should be uncommented at a time. See descriptions of methods to pick one.
    """
    #speaker_file = integration_test1()
    #speaker_file, save_path = integration_test2()
    speaker_file, save_path = integration_test3()
    
    if speaker_file:
        main(speaker_file, save_path=save_path, split_utterances=True)
