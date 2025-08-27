# vim: ft=make
# vim: tabstop=8
# vim: shiftwidth=8
# vim: noexpandtab

.PHONY: help

include Makefile.libs

run:		load validate ## Run all of the examples below
		@cd client_js_setstars && make run; cd ..
		@cd client_py_getrepo  && make run; cd ..
