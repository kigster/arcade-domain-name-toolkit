# vim: ft=make
# vim: tabstop=8
# vim: shiftwidth=8
# vim: noexpandtab

include ../Makefile.libs

.PHONY: help run validate

run:		validate ## Install deps
		@pip install arcadepy >/dev/null
		@echo "Authenticating against Arcade, to fetch info about this repo..."
		./arcade_get_repo.py | jq -C
