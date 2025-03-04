# Translation domain (name of .po and .mo files)
DOMAIN = messages
# Directory where localization files are stored
LOCALEDIR = locales
# Source code files to extract translations from
SRC = $(shell find src -type f -name "*.py")
# List of supported languages
LANGUAGES_FILE = $(LOCALEDIR)/languages.txt
LANGUAGES = $(shell cat $(LANGUAGES_FILE))

.PHONY: all update compile clean

# 1️⃣ Extract translatable strings and generate messages.pot
pot:
	xgettext --language=Python --keyword=_ --output=$(LOCALEDIR)/$(DOMAIN).pot $(SRC)

# 2️⃣ Create a new .po file for a new language
newlang:
	@if [ -z "$(language)" ] || [ -z "$(charset)" ]; then \
		echo "Please specify both short name for language and charset (e.g., make newlang language=ru charset=ru_RU.UTF-8)"; \
		exit 1; \
	fi
	@mkdir -p $(LOCALEDIR)/$(language)/LC_MESSAGES
	@echo "$(language)" >> $(LANGUAGES_FILE)
	@echo "Creating translation for language: $(language) with charset: $(charset)"
	msginit --input=$(LOCALEDIR)/$(DOMAIN).pot --output-file=$(LOCALEDIR)/$(language)/LC_MESSAGES/$(DOMAIN).po --locale=$(charset) --no-translator

# 3️⃣ Update existing .po files when source code changes
update: pot
	for lang in $(LANGUAGES); do \
		msgmerge --update --backup=none $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).po $(LOCALEDIR)/$(DOMAIN).pot; \
	done

# 4️⃣ Compile .po files into .mo files for gettext
compile:
	for lang in $(LANGUAGES); do \
		msgfmt --output-file=$(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo $(LOCALEDIR)/$$lang/LC_MESSAGES/$(DOMAIN).po; \
	done

# 5️⃣ Remove compiled .mo and .pot files
clean:
	rm -f $(LOCALEDIR)/*/LC_MESSAGES/$(DOMAIN).mo $(LOCALEDIR)/$(DOMAIN).pot

# Build executable
build:
	poetry run pyinstaller ./src/run_ui.py  --path ./src/ --clean --onefile --noconsole --add-data "locales:locales"