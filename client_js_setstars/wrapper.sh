#!/usr/bin/env bash

# Simple wrapper to catch Ctrl-C Interrupt more gracefully
trap 'echo -e "\033[1;32mUser cancelled Python Server, exiting.\033[0m\n\n"; exit 0' EXIT

npx run arcade_repo_set_stars.mjs

