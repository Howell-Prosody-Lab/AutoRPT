import os
import traceback
import textgrid
import re
import pandas as pd

class SpeakerFile:

    def __init__(self, textgrid_file_path=None, finaldict_file_path=None, wav_file_path=None, annot_filepath=None, existing_file=None, word_tier=None, phone_tier=None):
        '''
        Creates the SpeakerFile object using at least one of the keyword arguments. Extrapolates what other
        information is available from the files/file names and saves.
        :param textgrid_file_path: path-like string to a praat .TextGrid
        :param finaldict_file_path: path-like string to a csv output by AutoRPT
        :param wav_file_path: path-like string to a WAV file
        :param annot_filepath: path-like string to annotations CSV output by pull_human_anns_from_tgs
        :param existing_file: can be used to open from a text file
        '''
        if existing_file: self.read_from_txt2(existing_file)
        else:
            self.is_annotated = False
            self.file_version = "Regular"
            self.rpt_status = self.word_tier = self.word_tier_no = self.phone_tier = self.phone_tier_no = "Unknown"
            self.point_tier = self.point_tier_no = self.ideal_word_tier = self.ideal_phone_tier = "Unknown"
            if word_tier:
                self.word_tier = word_tier
            if phone_tier:
                self.phone_tier = phone_tier
            self.finaldict_filepath = self.final_dict = None
            self.annotations = self.annotator = self.annotations_filepath = None
            self.wav_filepath = self.textgrid_filepath = all_tiers = None
            self.wav_file_obj = self.textgrid_obj = None

            #Match name to a pattern to determine how the information should be derived
            first_existing_path = wav_file_path or textgrid_file_path or annot_filepath or finaldict_file_path
            if not first_existing_path:
                print("Must provide the SpeakerFile function with at least one argument.")
                quit(1)
            string_to_search = os.path.basename(first_existing_path)
            #Converting regex_definition into a single regular expression
            #This is done because the raw regex looks like this: (?P<grant_number>[0-9]{4})(?P<pairing_number>-?p[0-9]{2})(?P<race>-[A-Za-z][A-Za-z]?)?(?P<left_gender>-?[A-Za-z])(?P<right_gender>[A-Za-z])(?P<left_speaker_ID>[0-9]{2}[A-Za-z]{2})?(?P<right_speaker_ID>[0-9]{2}[A-Za-z]{2})?(?P<version>_[A-Za-z]+[0-9]?)?(?P<channel>[-_]([cC]h)?[12lLrR])(?P<annotator>[-_][A-Za-z]+)?(?P<file_extension>\.[A-Za-z]+)
            #Leave this part alone. You'll edit regex_definition.txt and read_regex() to customize.
            regex_def = pd.read_csv("regex_definition.txt", sep='\t', header=None)
            regex = r""
            for i, row in regex_def.iterrows():
                regex += '(?P<' #named groups
                regex += row[0]
                regex += '>'
                #print(row[0], row[2])
                regex += row[2]
                regex += (')')
                if row[1] == 'optional':
                    regex += '?'
            format_recognized = True  # true until proven false
            m = re.search(regex, s)
            if m:
                self.read_regex(m)
            else:
                format_recognized = False
                print("Matched no format")

            '''
            if not ending:
                print(f"Searching {self.the_rest} for regular expression defining channel and not finding one.")
                print("This file name implies a stereo file. In future please use a single-channel file \
                          with a file name ending in 1 or l for left channel, or 2 or r for right channel. \
                          Program will continue, but recommend you abort if stereo file.")
                self.channel = "unknown"
                format_recognized = False
            '''

            # derive variables from provided arguments
            print("Checking to see what files we provided...")
            if finaldict_file_path:
                self.add_final_dict(finaldict_file_path)

            if textgrid_file_path:
                try:
                    self.add_textgrid(textgrid_file_path)
                    all_tiers = self.textgrid_obj.getNames()
                    #print("Success")
                except AttributeError:
                    print(textgrid_file_path, "isn't a textgrid.")
                    print(traceback.format_exc())

            if annot_filepath:
                self.add_annotation_log(annot_filepath)
            elif 'nnotated' in string_to_search:
                self.is_annotated = True
                self.annotator = "Unavailable"
                self.annotation_filepath = None

            if 'redictions' in string_to_search:
                self.rpt_status = "AutoRPT"

            # summon Sound file from package
            if wav_file_path:
                self.add_wav(wav_file_path)

            if format_recognized and textgrid_file_path:
                print("Format recognized")
                point_tier, w_no, ph_no, pt_no = (self.parse_tiers(all_tiers))
                self.unpack_tg_output(point_tier, w_no, ph_no, pt_no)
            else:
                w_no = ph_no = word_tier = phone_tier = pt_no = point_tier = None
            if not format_recognized:
                stem = os.path.splitext(os.path.basename(first_existing_path))[0]
                self.base_filename = stem
                self.name_with_channel = stem
                self.name_with_channel_and_version = stem
                if self.word_tier == "Unknown":
                    print("\nThis file name or tier name does not match a recognized format. Enter tiers manually.")
                    self.word_tier = input("Enter the word tier name in the TextGrid: ")
                if self.phone_tier == "Unknown":
                    self.phone_tier = input("Enter the phone tier name in the TextGrid: ")


    #Methods that are basically part of init
    def unpack_tg_output(self, point_tier, w_no, ph_no, pt_no):
        '''
        Sets instance variables once textgrid is obtained
        :param point_tier: string name of point_tier
        :param w_no: int index of word_tier
        :param ph_no: int index of phone_tier
        :param pt_no: int index of point tier
        :return: none
        '''
        self.word_tier_no = w_no
        self.phone_tier_no = ph_no
        self.point_tier = point_tier
        self.point_tier_no = pt_no
              
    def parse_tiers(self, tiers):
        '''
        Given the tiers and what we think the word tier and phone tier should be,
        sets the variables to the actual word and phone tiers. If no likely candidate is found,
        the user is asked to choose.
        :param tiers: a list of strings representing the names of the tiers
        :return: the name of the last tier (supposedly the point tier) and the indices of the word, phone, and point tiers
        '''
        print("Parsing tiers...")
        print(tiers)
        if self.word_tier not in ("Unknown", None) and self.word_tier in tiers:
            pass  # already set from constructor argument; preserve it
        elif self.ideal_word_tier in tiers:
            self.word_tier = self.ideal_word_tier
            self.rpt_status = "not AutoRPT"
        elif "Text" in tiers:
            self.word_tier = "Text"
            self.rpt_status = "AutoRPT"
        else:
            self.word_tier = input(f"No word tier found (expecting {self.ideal_word_tier}). Enter word tier: ")
        if self.phone_tier not in ("Unknown", None) and self.phone_tier in tiers:
            pass  # already set from constructor argument; preserve it
        elif self.ideal_phone_tier in tiers:
            self.phone_tier = self.ideal_phone_tier
        elif 'phone' in tiers:
            self.phone_tier = 'phone'
        elif 'phones' in tiers:
            self.phone_tier = 'phones'
        elif 'Phone' in tiers:
            self.phone_tier = 'Phone'
        elif 'Phones' in tiers:
            self.phone_tier = 'Phones'
        else:
            print(tiers)
            self.phone_tier = input(f"No phone tier found (expecting {self.ideal_phone_tier}). Enter phone tier: ")
        return tiers[-1], tiers.index(self.word_tier), tiers.index(self.phone_tier), tiers.index(tiers[-1])

    def read_regex(self, m):
        '''
        Unpacks the file naming convention into information based on regex_definition.txt.
        You will customize this if you're not using an identical naming convention to me.
        See the ReadMe for how to customize regex_definition.txt.
        :param m: A match object created from a regex evaluation
        :return: none
        '''
        vars = m.groupdict() #dictionary mapping capture group names (k) to values
        whole_capture = m.groups(0)

        #some variables need cleaning up--this one has a -p in front we don't need
        self.pairing_number = vars['pairing_number'][-2:]

        #optional variables need to be nested in an if statement
        if vars['version']: #if version is not None
            self.version = vars['version'][1:] #then chop off the - and push to self.version

        if vars['race']:
            #Some variables need to be unpacked from shorthand
            v = vars['race'][1:]
            if v == "aa" or v == "a":
                self.variety = "African-American"
            elif v == "l":
                self.variety = "Latine"
            elif v == "m":
                self.variety = "mainstream"
            else:
                self.variety = v

        #Some pieces of title inform more than one variable
        if vars['annotator']:
            self.annotator = vars['annotator'][1:]
            self.is_annotated = True
        else:
            self.annotator = None
            self.is_annotated = False

        #Sometimes there are multiple ways to capture information.
        #The capture group allows for six ways to define channel.
        #This code normalizes them into 'left' and 'right'.
        temp_channel = vars['channel'][-1] #pull last character
        temp_gender = "" #this is a special tool that we'll use later
        lefts = ['1', 'L', 'l']
        rights = ['2', 'R', 'r']
        if temp_channel in lefts:
            self.channel = 'left'
            temp_gender = vars['left_gender'][-1]
            #the or means 'pick the first thing that's not None'
            #this says "if there's a left_speaker_ID, use that, if not, tack an -L onto pairing_number.
            self.speakerID = vars['left_speaker_ID'] or (self.pairing_number + '-L')
        elif temp_channel in rights:
            self.channel = 'right'
            temp_gender = vars['right_gender']
            self.speakerID = vars['right_speaker_ID'] or (self.pairing_number + '-R')
        else:
            print("No channel available", temp_channel)
            self.channel = None
            self.speakerID = None

        if temp_gender == "f":
            self.gender = "female"
        elif temp_gender == "m":
            self.gender = "male"
        elif temp_gender == "q" or temp_gender == "x":
            self.gender = "nonbinary"
        else:
            self.gender = temp_gender

        #different types of file names have different tier naming conventions too.
        #if MMT1--"if left_speaker_ID and right_speaker_ID exist"
        if vars['left_speaker_ID'] and vars['right_speaker_ID']:
            self.ideal_word_tier = speakerID + ' - words'
            self.ideal_phone_tier = speakerID + ' - phones'
            base_filename_end = m.end('right_speaker_ID') #also the "base" name ends in a different place
        else: #if MMT2
            if self.channel == "left":
                self.ideal_word_tier = "L - words"
                self.ideal_phone_tier = "L - phones"
            elif self.channel == "right":
                self.ideal_word_tier = "R - words"
                self.ideal_phone_tier = "R - phones"
                #print(self.ideal_word_tier)
            else:
                print("Cannot derive speaker ID or gender while channel is not defined.")
                speakerID = "unknown"
                gender = "unknown"
            base_filename_end = m.end('right_gender')

        st = m.start('grant_number')
        #These ways of retrieving the file name are derived from the variables too.
        self.base_filename = whole_capture[st:base_filename_end]
        self.name_with_channel = self.base_filename + vars['channel'][1:] #tack on channel
        self.name_with_channel_and_version = whole_capture[st:m.end('channel')]
        #like 3000-p09-aa-ff_sliced_ch1


    #String methods
    def __repr__(self):
        return (f"name up through version: {self.name_with_channel_and_version}\n" +
                f"name with no anything including channel: {self.base_filename}\n" +
                f"name plus channel but no version: {self.name_with_channel}\n"+
                f"textgrid word tier: {self.word_tier} (at index {self.word_tier_no})\n" +
                f"textgrid phone tier: {self.phone_tier} (at index {self.phone_tier_no})\n" +
                f"textgrid point tier: {self.point_tier} (at index {self.point_tier_no})\n" +
                f"channel: {self.channel}\n" +
                f"experiment pairing: {self.pairing_number}\n" +
                f"speaker ID: {self.speakerID}\n" +
                f"gender: {self.gender}\n" +
                f"variety: {self.variety}\n" +
                f"RPT status: {self.rpt_status}\n" +
                f"Annotated: {str(self.is_annotated)}\n" +
                f"Annotator: {self.annotator}\n" +
                f"Regular file vs sliced vs map: {self.file_version}\n" +
                f"Textgrid filepath: {self.textgrid_filepath}\n" +
                f"Wav filepath: {self.wav_filepath}")
    def contents(self):
        print(self.__repr__())
    def __str__(self):
        return self.name_with_channel_and_version

    #checkers and setters
    def has_annotation_log(self):
        if not self.is_annotated or not self.annotator or self.annotator == "Unavailable" or self.annotator == "nan":
            return False
        else: return True

    def has_final_dict(self):
        if not self.finaldict_filepath: return False
        else: return True

    def has_wav(self):
        try:
            if self.wav_file_obj and self.wav_file_obj != "placeholder": return True
            else: return False
        except AttributeError:
            self.wav_file_obj = "placeholder"
            return False

    def has_textgrid(self):
        #Returns Boolean
        try:
            if self.textgrid_obj and self.textgrid_obj != "placeholder": return True
            else: return False
        except AttributeError:
            self.textgrid_obj = "placeholder"
            return False

    def add_annotation_log(self, annot_filepath):
        '''
        Given the filepath, adds an annotation log to the object in the form of a pandas dataframe.
        :param annot_filepath: path-like string
        :return: none
        '''
        #print("Open add_annotation_log")
        self.annotation_filepath = annot_filepath
        self.is_annotated = True
        try:
            self.annotations = pd.read_csv(annot_filepath)
            annotator = self.annotations.iloc[0].at["Annotator"]
            #print(annotator)
            gabriella = ['1213p04ma24gh28nc_1']

            isabel = ['1213p08mx05nc22cm_2', '1213p09mx06mt23gb_1', '1213p07mx04jd21cc_2']

            sam = ['1213p06ma26cm32mm_2', '1213p03fm03sg07gl_1']

            sally = ['1213p41mx60yr79ms_sliced_ch1', '1213p48mx92zr82pv_sliced_ch2', '1213p41mx60yr79ms_sliced_ch2',
                     '1213p48mx92zr82pv_sliced_ch1', '1213p45mx02cm73nc_sliced_ch1', '1213p42mx50nb35ba_sliced_ch1',
                     '1213p45mx02cm73nc_sliced_ch2']

            kevin = ['1213p35ma74cr15kd_ch1', '1213p35ma74cr15kd_ch2', '1213p38ma71re67jd_ch1', '1213p38ma71re67jd_ch2',
                     '1213p46mx91jf72rb_ch1', '1213p46mx91jf72rb_ch2']
            print(annotator)
            #print(self.name_with_channel)
            print(self.name_with_channel_and_version)
            if annotator and annotator != "nan" and annotator != "NaN":
                #print("path 1")
                self.annotator = annotator
                #print(self.annotator == "nan")
            if "kai" in self.the_rest:
                self.annotator="Kai"
            elif "Kevin" in self.the_rest or "Kevin" in self.point_tier:
                print("Found Kevin")
                self.annotator = "Kevin"
            elif "map" in self.file_version:
                self.annotator = "DJ"
            elif self.name_with_channel in isabel:
                self.annotator = "Isabel"
            elif self.name_with_channel in sam:
                self.annotator = "Sam"
            elif self.name_with_channel in gabriella or self.name_with_channel_and_version in gabriella:
                self.annotator = "Gabriella"
            elif self.name_with_channel_and_version in sally:
                print("Found Sally")
                self.annotator = "Sally"
            elif self.name_with_channel in kevin:
                print("Found Kevin")
                self.annotator = "Kevin"
            else:
                print("Couldn't find an annotator")

            print(self.annotator)

            if (annotator != self.annotator) and self.annotator in ["Sally", "Kevin", "Sam", "Gabriella", "Isabel", "DJ", "Kai", "Kevin"]:
                #print("we have got to this branch")
                temp = self.annotations.copy()
                for i, row in temp.iterrows():
                    temp.at[i, 'Annotator'] = self.annotator
                self.annotations = temp
                temp.to_csv(self.annotation_filepath)
        except FileNotFoundError:
            print(f"Could not find path at {annot_filepath}, skipping annotations read")
            self.annotations = None
            self.annotator = "Unavailable"

    def add_final_dict(self, final_dict_filepath):
        '''
        Given the path, adds a phonetic dictionary as created by autorpt to the object
        as a pandas dataframe.
        :param final_dict_filepath:
        :return:
        '''
        print("Attempting to add phonetics measures")
        self.finaldict_filepath = final_dict_filepath
        try:
            self.final_dict = pd.read_csv(final_dict_filepath)
        except FileNotFoundError:
            print(f"Could not find path at {final_dict_filepath}, skipping final_dict read")
            final_dict = None

    def add_textgrid(self, textgrid_file_path):
        '''
        Given the filepath, adds a textgrid object to the file.
        Filepath must remain valid--textgrid object cannot pickle.
        :param textgrid_file_path: path-like string
        :return: none
        '''
        print("Attempting to add textgrid")
        self.textgrid_filepath = textgrid_file_path
        # summon textgrid files from package
        try:
            self.textgrid_obj = textgrid.TextGrid.fromFile(textgrid_file_path)
            all_tiers = [t.name for t in self.textgrid_obj.tiers]
            #you'd think this could be done in one line but "missing 5 required positional arguments"
            point_tier, w_no, ph_no, pt_no = self.parse_tiers(all_tiers)
            self.unpack_tg_output(point_tier, w_no, ph_no, pt_no)
            print("Textgrid successfully added")
        except FileNotFoundError:
            print("TextGrid file not found for",self.name_with_channel_and_version)
            from tkinter import filedialog
            file = filedialog.askopenfilename(title="Select TextGrid File", filetypes=[("TextGrid files", "*.TextGrid")])
            self.add_textgrid(file)
        except:
            print("Unable to read textgrid, skipping")
            print("Path exists?",os.path.exists(textgrid_file_path))
            print(traceback.format_exc())

    def add_wav(self, wav_file_path):
        '''
        Give the filepath, adds a parselmouth Sound object to the file.
        Path must remain valid--Sound object does not pickle.
        :param wav_file_path: path-like string
        :return: none
        '''
        try:
            import parselmouth
            self.wav_filepath = wav_file_path
            self.wav_file_obj = parselmouth.Sound(wav_file_path)
        except FileNotFoundError:
            print("Wav file not found.")
        except:
            print("Unable to read Sound file, skipping")
            #print("Path exists?", os.path.exists(wav_file_path))
            print(traceback.format_exc())
    #I/O
    def __getstate__(self):
        '''
        Copy the object's state from self.__dict__ which contains
        all our instance attributes.
        :return: a dictionary containing all picklable instance variables, used for pickling (obviously)
        '''
        # Always use the dict.copy() method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        try:
            if self.wav_file_obj:
                del state['wav_file_obj']
        except AttributeError:
            pass
        try:
            if self.textgrid_obj:
                del state['textgrid_obj']
        except AttributeError:
            pass

        return state

    def __setstate__(self, state):
        '''
        Restores instance attributes.
        :param state: dictionary containing all picklable instance variables
        :return: none
        '''
        # Restore instance attributes
        self.__dict__.update(state)
        # Restore unpicklable files by following filepaths
        if self.wav_filepath:
            self.add_wav(self.wav_filepath)
        if self.textgrid_filepath:
            self.add_textgrid((self.textgrid_filepath))


    @classmethod
    def read_from_txt(cls, existing_file):
        cls.savepath = existing_file
        def read_helper(line, tag):
            temp = line.split('= ')
            temp1 = temp[1].strip()
            if temp[0] != tag: raise Exception(f"{temp[0]} != {tag}")
            elif temp1 == "None": return None
            elif temp1 == "True": return True
            elif temp1 == "False": return False
            else: return temp1

        with open(existing_file, 'r') as f:
            f.readline()
            classname = f.readline()
            if classname.split('"')[1] != 'SpeakerFile': raise Exception("classtype")
            print(f.readline().split('= '))
            cls.name_with_channel_and_version = read_helper(f.readline(), "name_with_channel_and_version")
            cls.name_with_channel = read_helper(f.readline(), "name_with_channel")
            cls.base_filename = read_helper(f.readline(),"base_filename")
            cls.channel = read_helper(f.readline(), "channel")
            cls.pairing_number = read_helper(f.readline(), "pairing_number")
            cls.speakerID = read_helper(f.readline(), "speakerID")
            cls.textgrid_filepath = read_helper(f.readline(), "textgrid_filepath")
            cls.textgrid_filename = read_helper(f.readline(), "textgrid_filename")
            cls.word_tier = read_helper(f.readline(), "word_tier")
            word_tier_no = f.readline().split('= ')[1]
            cls.word_tier_no = int(word_tier_no) if word_tier_no != "None" else None
            cls.phone_tier = read_helper(f.readline(), "phone_tier")
            phone_tier_no = f.readline().split('= ')[1]
            cls.phone_tier_no = int(phone_tier_no) if phone_tier_no != "None" else None
            cls.point_tier = read_helper(f.readline(), "point_tier")
            point_tier_no = f.readline().split('= ')[1]
            cls.point_tier_no = int(point_tier_no) if point_tier_no != "None" else None
            cls.gender = read_helper(f.readline(),"gender")
            cls.variety = read_helper(f.readline(), "variety")
            cls.finaldict_filepath = read_helper(f.readline(), "finaldict_filepath")
            cls.finaldict_filename = read_helper(f.readline(), "finaldict_filename")
            cls.wav_filepath = read_helper(f.readline(),"wav_filepath")
            cls.annotations_filepath = read_helper(f.readline(), "annotations_filepath")
            cls.is_annotated = read_helper(f.readline(), "annotated")
            cls.annotator = read_helper(f.readline(), "annotator")
            cls.file_version = read_helper(f.readline(), "file_version")
            cls.rpt_status = read_helper(f.readline(), "rpt_status")

            if cls.wav_filepath and os.path.exists(cls.wav_filepath):
                cls.add_wav(cls, cls.wav_filepath)
            else:
                cls.wav_file_obj = "placeholder"
                cls.wav_filepath = None

            if cls.textgrid_filepath and os.path.exists(cls.textgrid_filepath):
                cls.textgrid_obj = textgrid.TextGrid.fromFile(cls.textgrid_filepath)

            if cls.finaldict_filepath and os.path.exists(cls.finaldict_filepath):
                cls.final_dict = pd.read_csv(cls.finaldict_filepath)
            else: cls.finaldict_filepath = None

            if cls.annotations_filepath and os.path.exists(cls.annotations_filepath):
                cls.annotations = pd.read_csv(cls.annotations_filepath)
            else: cls.annotations = cls.annotations_filepath = None
    def read_from_txt2(self, existing_file):
        self.savepath = existing_file
        def read_helper(line, tag):
            temp = line.split('= ')
            temp1 = temp[1].strip()
            if temp[0] != tag: raise Exception(f"{temp[0]} != {tag}")
            elif temp1 == "None": return None
            elif temp1 == "True": return True
            elif temp1 == "False": return False
            else: return temp1

        with open(existing_file, 'r') as f:
            f.readline()
            classname = f.readline()
            if classname.split('"')[1] != 'SpeakerFile': raise Exception("classtype")
            print(f.readline().split('= '))
            self.name_with_channel_and_version = read_helper(f.readline(), "name_with_channel_and_version")
            self.name_with_channel = read_helper(f.readline(), "name_with_channel")
            self.base_filename = read_helper(f.readline(),"base_filename")
            self.channel = read_helper(f.readline(), "channel")
            self.pairing_number = read_helper(f.readline(), "pairing_number")
            self.speakerID = read_helper(f.readline(), "speakerID")
            self.textgrid_filepath = read_helper(f.readline(), "textgrid_filepath")
            self.textgrid_filename = read_helper(f.readline(), "textgrid_filename")
            self.word_tier = read_helper(f.readline(), "word_tier")
            word_tier_no = f.readline().split('= ')[1]
            self.word_tier_no = int(word_tier_no) if word_tier_no != "None" else None
            self.phone_tier = read_helper(f.readline(), "phone_tier")
            phone_tier_no = f.readline().split('= ')[1]
            self.phone_tier_no = int(phone_tier_no) if phone_tier_no != "None" else None
            self.point_tier = read_helper(f.readline(), "point_tier")
            point_tier_no = f.readline().split('= ')[1]
            self.point_tier_no = int(point_tier_no) if point_tier_no != "None" else None
            self.gender = read_helper(f.readline(),"gender")
            self.variety = read_helper(f.readline(), "variety")
            self.finaldict_filepath = read_helper(f.readline(), "finaldict_filepath")
            self.finaldict_filename = read_helper(f.readline(), "finaldict_filename")
            self.wav_filepath = read_helper(f.readline(),"wav_filepath")
            self.annotations_filepath = read_helper(f.readline(), "annotations_filepath")
            self.is_annotated = read_helper(f.readline(), "annotated")
            self.annotator = read_helper(f.readline(), "annotator")
            self.file_version = read_helper(f.readline(), "file_version")
            self.rpt_status = read_helper(f.readline(), "rpt_status")

            if self.wav_filepath and os.path.exists(self.wav_filepath):
                self.add_wav(self.wav_filepath)
            else: self.wav_file_obj = self.wav_filepath = None

            if self.textgrid_filepath and os.path.exists(self.textgrid_filepath):
                self.add_textgrid(self.textgrid_filepath)
            else: self.textgrid_filepath = self.textgrid_obj = None

            if self.finaldict_filepath and os.path.exists(self.finaldict_filepath):
                self.add_final_dict(self.finaldict_filepath)
            else: self.finaldict_filepath = self.finaldict_filename = None

            if self.annotations_filepath and os.path.exists(self.annotations_filepath):
                self.add_annotation_log(self.annotations_filepath)
            else: self.annotations = self.annotations_filepath = None

        #print(self.__repr__())

    def write_to_txt(self, f):
            """
            Write the current state into a Praat-format TextGrid file.
            :param f: may be a file object to write to, or a string naming a path to open
            for writing.
            :returns: none
            """
            import codecs
            sink = f if hasattr(f, 'write') else codecs.open(f, 'w', 'UTF-8')
            print('File type = "ooTextFile"', file=sink)
            print('Object class = "SpeakerFile"\n', file=sink)
            print('name_with_channel_and_version= {0}'.format(self.name_with_channel_and_version), file=sink)
            print('name_with_channel= {0}'.format(self.name_with_channel), file=sink)
            print('base_filename= {0}'.format(self.base_filename), file=sink)
            print('channel= {0}'.format(self.channel), file=sink)
            print('pairing_number= {0}'.format(self.pairing_number), file=sink)
            print('speakerID= {0}'.format(self.speakerID), file=sink)
            print('textgrid_filepath= {0}'.format(self.textgrid_filepath), file=sink)
            print('textgrid_filename= {0}'.format(self.textgrid_filename), file=sink)
            print('word_tier= {0}'.format(self.word_tier), file=sink)
            print('word_tier_index= {0}'.format(self.word_tier_no), file=sink)
            print('phone_tier= {0}'.format(self.phone_tier), file=sink)
            print('phone_tier_index= {0}'.format(self.phone_tier_no), file=sink)
            print('point_tier= {0}'.format(self.point_tier), file=sink)
            print('point_tier_index= {0}'.format(self.point_tier_no), file=sink)
            print('gender= {0}'.format(self.gender), file=sink)
            print('variety= {0}'.format(self.variety), file=sink)
            print('finaldict_filepath= {0}'.format(self.finaldict_filepath), file=sink)
            print('finaldict_filename= {0}'.format(self.finaldict_filename), file=sink)
            print('wav_filepath= {0}'.format(self.wav_filepath), file=sink)
            print('annotations_filepath= {0}'.format(self.annotations_filepath), file=sink)
            print('annotated= {0}'.format(self.is_annotated), file=sink)
            print('annotator= {0}'.format(self.annotator), file=sink)
            print('file_version= {0}'.format(self.file_version), file=sink)
            print('rpt_status= {0}'.format(self.rpt_status), file=sink)
            sink.close()
            print(f"File written to {f}")


if __name__ == '__main__':
    textgrid_path = "G:\\Shared drives\\Prosody\\Acoustic Data\\human annotations\\one textgrids\\kai 1213p28fm42lw41mc_sliced_ch2_Predictions_adjusted.TextGrid"
    annotations_path = "G:\\Shared drives\\Prosody\\Acoustic Data\\human annotations\\one textgrids\\kai 1213p20ma23rk29mk_sliced_ch2_annotations.csv"
    write_path = "G:\\Shared drives\\Prosody\\Acoustic Data\\human annotations\\one textgrids\\1213p20ma23rk29mk_sliced_ch2_annotations.SpeakerFile"
    #s = SpeakerFile(textgrid_filepath=textgrid_path)
    #s = SpeakerFile(annot_filepath=annotations_path)
    #s = SpeakerFile(textgrid_filepath=textgrid_path, annot_filepath=annotations_path)
    s = SpeakerFile(existing_file=write_path)
    print(s.__repr__())
    #s.write(write_path)
