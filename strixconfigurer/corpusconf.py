import json
import os
import glob
import logging
import importlib.machinery

import yaml
from yaml.loader import SafeLoader

class CorpusConfig:

    def __init__(self, settings_dir):
        self.logger = logging.getLogger(__name__)
        self.settings_dir = settings_dir
        self._all_config_files = self._get_all_config_files()
        self.corpora_protected = self._get_protected()
        self._word_attributes = self._get_attributes("word_attributes")
        self._struct_attributes = self._get_attributes("struct_attributes")
        self._text_attributes = self._get_attributes("text_attributes")
        self._type_info = self._load_type_info()
        self._struct_elems = self._load_struct_elems()

    def get_modes(self):
        modes = {}
        for filename in glob.glob(os.path.join(self.settings_dir, "modes/*")):
            with open(filename) as file:
                mode = yaml.load(file, Loader=SafeLoader)
                modes[mode["name"]] = mode
        return modes

    def get_corpus_conf(self, corpus_id):
        """
        get all information about corpus_id
        """
        return self._all_config_files[corpus_id]

    def is_corpus(self, corpus_id):
        """
        checks if corpus_id is an actual configured corpus
        """
        return corpus_id in self._all_config_files

    def get_word_attribute(self, attr_name):
        return self._word_attributes[attr_name]

    def get_word_attributeX(self, attr_name):
        with open(os.path.join(self.settings_dir, "attributes/positional/"+attr_name+".yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

    def get_word_attributes(self):
        return self._word_attributes

    def get_struct_attribute(self, attr_name):
        return self._struct_attributes[attr_name]

    def get_struct_attributeX(self, attr_name):
        with open(os.path.join(self.settings_dir, "attributes/structural/"+attr_name+".yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

    def get_struct_attributes(self):
        return self._struct_attributes

    def get_text_attribute(self, attr_name):
        return self._text_attributes[attr_name]

    def get_text_attributeX(self, attr_name):
        with open(os.path.join(self.settings_dir, "attributes/structural/"+attr_name+".yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

    def get_text_attributes_by_corpora(self):
        """
        :return: a dict containing all text attributes by corpora
        """
        text_attributes = {}
        text_attributes_list = {}
        for key, conf in self._all_config_files.items():
            try:
                tempDict = {}
                for attr_dict in conf["analyze_config"]["text_attributes"]:
                    for attr_name, attr in attr_dict.items():
                        if type(attr) is str:
                            attr = self.get_text_attributeX(attr)
                        tempDict[attr_name] = attr
                        text_attributes_list[attr_name] = attr
                text_attributes[key] = tempDict
                        
            except KeyError:
                self.logger.info("No text attributes for corpus: %s" % key)
                continue
            if "title" in text_attributes[key]:
                del text_attributes[key]["title"]
        # TODO fix hardcoded
        text_attributes_list['yearR'] = {'name': 'yearR', 'translation_name': {'swe': 'År', 'eng': 'Year'}}
        # TODO WHY do we need this???
        text_attributes["litteraturbanken"] = text_attributes_list
        return text_attributes

    def get_text_attributes(self):
        return self._text_attributes

    def is_ranked(self, word_attribute):
        try:
            return self._word_attributes[word_attribute].get("ranked", False)
        except KeyError:
            raise ValueError("\"" + word_attribute + "\" is not configured")

    def get_type_info(self):
        return self._type_info

    def get_struct_elem(self, elem):
        return self._struct_elems[elem]

    def _load_type_info(self):
         with open(os.path.join(self.settings_dir, "attributes/types.yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

    def _load_struct_elems(self):
        with open(os.path.join(self.settings_dir, "attributes/struct_elems.yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

    def _get_all_config_files(self):
        config_files = {}
        for file in glob.glob(self._get_config_file("*")):
            key = os.path.splitext(os.path.basename(file))[0]
            config_files[key] = self._fetch_corpus_conf(key)
        return config_files
    
    def _get_protected(self):
        config_protected = {}
        for file in glob.glob(self._get_config_file("*")):
            key = os.path.splitext(os.path.basename(file))[0]
            config_protected[key] = self._fetch_corpus_conf(key).get("protected", False)
        return config_protected

    def _fetch_corpus_conf(self, corpus_id, config_type="corpora"):
        """
        Open requested corpus settings file
        :param corpus_id: id of corpus to fetch
        :return: a dict containing configuration for corpus
        """
        config_file = self._get_config_file(corpus_id, config_type)
        try:
            config_obj = yaml.load(open(config_file), Loader=SafeLoader)
        except Exception:
            self.logger.error("Could not read config file: " + config_file)
            raise

        return config_obj

    def _get_config_file(self, corpus_id, config_type="corpora"):
        return os.path.join(self.settings_dir, config_type, corpus_id + ".yaml") 

    def _get_attributes(self, attr_type):
        with open(os.path.join(self.settings_dir, "attributes", attr_type + ".yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

    def get_folders_info(self):
        with open(os.path.join(self.settings_dir, "all_folders.yaml")) as file:
            return yaml.load(file, Loader=SafeLoader)

