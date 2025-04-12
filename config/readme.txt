
1. If you add items to app_config.toml, make sure to add to src/utils/config_loader.py

Example:
Add :
[mynewsection]
new_config = "joedoe"

src/utils/config__loader.py
self.MYNEWSECTION_NEW_CONFIG = config["mynewsection"]["new_config"]    


