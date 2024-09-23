# Strix config configurer

This repo uses five types of files:
- Type config
- Attribute config
- Corpora templates
- Corpora configs
- Plugins

Attribute configs refer to types, corpora templates and configs refer to attributes from the attribute 
configs.

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




