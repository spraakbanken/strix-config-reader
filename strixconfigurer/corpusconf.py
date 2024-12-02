import os
import glob
import logging

import yaml
from yaml.loader import SafeLoader

class CorpusConfig:

    def __init__(self, settings_dir):
        self.logger = logging.getLogger(__name__)
        self.settings_dir = settings_dir
        self._all_config_files = self._get_all_config_files()
        self._type_info = self._load_type_info()
        self._struct_elems = self._load_struct_elems()
        self._modes = self._load_modes()
        self._word_attributes = self._load_attributes("positional")
        self._struct_attributes = self._load_attributes("structural")

    def get_modes(self):
        return self._modes

    def _load_modes(self):
        modes = {}
        for filename in glob.glob(os.path.join(self.settings_dir, "modes/*")):
            with open(filename) as file:
                mode = yaml.load(file, Loader=SafeLoader)
                mode_name = next(iter(mode))
                modes[mode_name] = mode[mode_name]
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

    def get_struct_attribute(self, attr_name):
        return self._struct_attributes[attr_name]

    def _load_attributes(self, type):
        attrs = {}
        for path in glob.glob(os.path.join(self.settings_dir, f"attributes/{type}/*.yaml")):
            with open(path) as file:
                attr = yaml.load(file, Loader=SafeLoader)
                attr_name = os.path.splitext(os.path.basename(path))[0]
                attrs[attr_name] = attr
        return attrs

    # TODO fix name
    def get_text_attributes_list(self):
        text_attributes_list = {}
        for key, conf in self._all_config_files.items():
            for attr_dict in conf["analyze_config"].get("text_attributes", []):
                for attr_name, attr in attr_dict.items():
                    if type(attr) is str:
                        attr = self.get_struct_attribute(attr)
                    # TODO  this overwrites previous instances of the value and does not check for  mismatches
                    text_attributes_list[attr_name] = attr
        text_attributes_list['yearR'] = {'name': 'yearR', 'translation_name': {'swe': 'År', 'eng': 'Year'}}
        return text_attributes_list


    def get_text_attributes_by_corpora(self):
        """
        :return: a dict containing all text attributes by corpora
        """
        text_attributes = {}
        for key, conf in self._all_config_files.items():
            try:
                attrs = {}
                for attr_dict in conf["analyze_config"]["text_attributes"]:
                    for attr_name, attr in attr_dict.items():
                        if type(attr) is str:
                            attr = self.get_struct_attribute(attr)
                        attrs[attr_name] = attr
                text_attributes[key] = attrs

            except KeyError:
                self.logger.info("No text attributes for corpus: %s" % key)
                continue
            if "title" in text_attributes[key]:
                del text_attributes[key]["title"]
        return text_attributes

    def get_type_info(self):
        return self._type_info

    def get_struct_elem(self, elem):
        return self._struct_elems[elem]

    def get_protected(self):
        config_protected = {}
        for key, conf in self._all_config_files.items():
            config_protected[key] = conf.get("protected", False)
        return config_protected

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

    def _fetch_corpus_conf(self, corpus_id):
        """
        Open requested corpus settings file
        :param corpus_id: id of corpus to fetch
        :return: a dict containing configuration for corpus
        """
        config_file = self._get_config_file(corpus_id)
        try:
            config_obj = yaml.load(open(config_file), Loader=SafeLoader)
        except Exception:
            self.logger.error("Could not read config file: " + config_file)
            raise

        return config_obj

    def _get_config_file(self, corpus_id):
        return os.path.join(self.settings_dir, "corpora", corpus_id + ".yaml")
