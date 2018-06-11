# Strix config configurer

This repo uses five types of files:
- Type config
- Attribute config
- Corpora templates
- Corpora configs
- Plugins

Attribute configs refer to types, corpora templates and configs refer to attributes from the attribute 
configs or plugins.

### Types

Types are located in `<settings_dir>/config/attributes/types.json`

### Attributes

Attributes are located in `<settings_dir>/config/attributes/<attribute_type>_attributes.json`

where attribute type can be `word`, `struct` or `text`.

### Corpora templates

Located in `<settings_dir>/config/corpora_templates/<name>.json`

The corpora configs can then use a template using the `parents`-key.

###  Corpora configs

Located in `<settings_dir>/config/corpora/<corpus_id>.json`.

### Plugins

Plugins are Python files in `<settings_dir>/strixplugins/<plugin_name>.py`

The plugin name can be anything and is used in the corpus config (currently not supported by templates).

```
{
    "corpus_id": "something",
    ...
    "token_lookup_plugin": "someplugin",
    "pipeline_plugin": "someplugin"
}
```

would load the file  `<settings_dir>/strixplugins/someplugin.py` and expect that the file includes
both a function `process_text_attributes` and `process_token_lookup` (see below).

#### Pipeline plugin

`process_text_attributes` from the given `pipeline_plugin` is called during parsing, where the plugin 
may add or remove (for example combine) text attributes.

```
def process_text_attributes(text_attributes):
  if "something" in text_attributes:
    text_attributes["something_else"] = text_attributes["something"]
```

#### Web API plugin 

`process_token_lookup` from the module given by `token_lookup_plugin` is called from the web api to 
transform the `token_lookup`:

```
def process_token_lookup(text_attributes, token_lookup):
    something = text_attributes.get("something")
    for token in token_lookup.values():
        if something:
            token["attrs"]["sentence"]["attrs"]["something"] = something
```




