# vim: ft=make
# vim: tabstop=8
# vim: shiftwidth=8
# vim: noexpandtab

include ../Makefile.libs

.PHONY: help build run

build:		## Install deps
		yarn install

run:		build validate ## Execute the logic in the JavaScript file, and star the repo!
		bash wrapper.sh # wrwapper executes npx run, but traps ctrl-c from the user.
		

