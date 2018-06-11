import json
import os
import glob
import logging
import importlib.machinery


class CorpusConfig:

    def __init__(self, settings_dir):
        self.logger = logging.getLogger(__name__)
        self.settings_dir = settings_dir
        self._all_config_files = self._get_all_config_files()
        self._word_attributes = self._get_attributes("word_attributes")
        self._struct_attributes = self._get_attributes("struct_attributes")
        self._text_attributes = self._get_attributes("text_attributes")
        self._type_info = self._load_type_info()
        self._plugin_cache = {}

    def get_plugin(self, plugin_name):
        if plugin_name not in self._plugin_cache:
            plugin_path = os.path.join(self.settings_dir, "strixplugins", plugin_name + ".py")
            module_name = "strixplugins." + plugin_name
            plugin = importlib.machinery.SourceFileLoader(module_name, plugin_path).load_module()
            self._plugin_cache[plugin_name] = plugin
        return self._plugin_cache[plugin_name]

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

    def get_word_attributes(self):
        return self._word_attributes

    def get_struct_attribute(self, attr_name):
        return self._struct_attributes[attr_name]

    def get_struct_attributes(self):
        return self._struct_attributes

    def get_text_attribute(self, attr_name):
        return self._text_attributes[attr_name]

    def get_text_attributes_by_corpora(self):
        """
        :return: a dict containing all text attributes by corpora
        """
        text_attributes = {}
        for key, conf in self._all_config_files.items():
            try:
                text_attributes[key] = dict((attr, self._text_attributes[attr]) for attr in conf["analyze_config"]["text_attributes"])
            except KeyError:
                self.logger.info("No text attributes for corpus: %s" % key)
                continue
            if "title" in text_attributes[key]:
                del text_attributes[key]["title"]

        # TODO WHY do we need this???
        text_attributes["litteraturbanken"] = []
        return text_attributes

    def get_text_attributes(self):
        return self._text_attributes

    def is_ranked(self, word_attribute):
        try:
            return self._word_attributes[word_attribute].get("ranked", False)
        except KeyError:
            raise ValueError("\"" + word_attribute + "\" is not configured")

    def is_object(self, path):
        try:
            if path[-1] in self._struct_attributes:
                return not self._struct_attributes[path[-1]].get("index_in_text", True)
            return False
        except KeyError:
            raise ValueError("\"" + ".".join(path) + "\" is not configured")

    def get_type_info(self):
        return self._type_info

    def _load_type_info(self):
        type_file = os.path.join(self.settings_dir, "config/attributes/types.json")
        return json.load(open(type_file))

    def _get_all_config_files(self):
        config_files = {}
        for file in glob.glob(self._get_config_file("*")):
            key = os.path.splitext(os.path.basename(file))[0]
            config_files[key] = self._fetch_corpus_conf(key)
        return config_files

    def _fetch_corpus_conf(self, corpus_id, config_type="corpora"):
        """
        Open requested corpus settings file and recursively fetch and merge
        with parent config file, if there is one.
        :param corpus_id: id of corpus to fetch
        :return: a dict containing configuration for corpus
        """
        config_file = self._get_config_file(corpus_id, config_type)
        try:
            config_obj = json.load(open(config_file))
        except Exception:
            self.logger.error("Could not read config file: " + config_file)
            raise

        parents = config_obj.get("parents", [])
        for parent in parents:
            parent_obj = self._fetch_corpus_conf(parent, config_type="corpora_templates")
            _merge_configs(config_obj, parent_obj)
        return config_obj

    def _get_config_file(self, corpus_id, config_type="corpora"):
        return os.path.join(self.settings_dir, "config", config_type, corpus_id + ".json")

    def _get_attributes(self, attr_type):
        return json.load(open(os.path.join(self.settings_dir, "config", "attributes", attr_type + ".json")))


def _merge_configs(target, source):
    """
    Merge two corpus configurations.
    Moves attributes from source to target, so any definitions in both will
    be overwritten by source.
    :return: A new corpus configuration.
    """
    for k, v in source.items():
        if k in target:
            if k == "analyze_config":
                for k2, v2 in source["analyze_config"].items():
                    if k2 in ["text_attributes", "word_attributes"]:
                        if k2 not in target["analyze_config"]:
                            target["analyze_config"][k2] = []
                        v2.extend(target["analyze_config"][k2])
                        target["analyze_config"][k2] = v2
                    elif k2 == "struct_attributes":
                        for k3, v3 in source["analyze_config"]["struct_attributes"].items():
                            if "struct_attributes" not in target["analyze_config"]:
                                target["analyze_config"]["struct_attributes"] = {}
                            elif k3 in target["analyze_config"]["struct_attributes"]:
                                v3.extend(target["analyze_config"]["struct_attributes"][k3])
                            target["analyze_config"]["struct_attributes"][k3] = v3
                    else:
                        raise ValueError("Key: " + k + "." + k2 + ", not allowed in parent configuration.")
        else:
            target[k] = v
