SHELL := /bin/bash

PYTHON_LIB_DIR?=/usr/lib/python3/dist-packages
DOC_DIR?=/usr/share/doc
ICON_DIR?=/usr/share/icons
SHARE_DIR?=/usr/share
SYSTEMD_DIR?=/usr/lib/systemd/user
DEST_DIR?=

FILES := $(shell find ledger/* -type f ! -path "**/__pycache__/*" ! -path "**/.git" ! -path "**/.gitignore" ! -path "**/LICENSE" ! -path "**/README.md" ! -path "**/static/*" ! -path "**/media/*")


ifdef VERBOSE
  Q :=
else
  Q := @
endif


clean:
	$(Q)rm -rf ./build
	$(Q)rm -rf ./ledger/static
	$(Q)find ledger -depth -name __pycache__ -exec rm -rf {} \;


print-%:
	@echo $*=$($*)


venv:
	$(Q)/usr/bin/python3 -m venv venv
	$(Q)( \
		source venv/bin/activate; \
		pip install -r requirements.txt; \
	)
	$(Q)ln -fs ${PYTHON_LIB_DIR}/gi venv/lib/python3*/site-packages/
	$(Q)ln -fs ${PYTHON_LIB_DIR}/dbus venv/lib/python3*/site-packages/
	$(Q)for f in ${PYTHON_LIB_DIR}/_dbus*; do \
		ln -fs $$f venv/lib/python3*/site-packages/; \
	done


test:
	$(Q)cd ledger && python manage.py test

ledger/static:
	$(Q)python ledger/manage.py collectstatic -c --noinput


deb: test build/package/DEBIAN/control
	$(Q)fakeroot dpkg-deb -b build/package build/ledger.deb
	$(Q)lintian -Ivi --suppress-tags embedded-javascript-library,font-outside-font-dir,font-in-non-font-package,desktop-command-not-in-package build/ledger.deb
	@echo "ledger.deb completed."


deb-sig: deb
	$(Q)dpkg-sig -s builder build/ledger.deb
	@echo "Signed ledger.deb."


install: ledger/static build/copyright build/changelog.Debian.gz build/package/DEBIAN build/conf/ledger.desktop
	$(Q)for f in ${FILES}; do \
		install -Dm 0644 $$f "${DEST_DIR}${SHARE_DIR}"/$$f; \
	done
	$(Q)for f in $(shell find ledger/static/* -type f); do \
		install -Dm 0644 $$f "${DEST_DIR}${SHARE_DIR}"/$$f; \
	done

	$(Q)install -Dm 0644 uwsgi.ini "${DEST_DIR}${SHARE_DIR}"/ledger/uwsgi.ini

	$(Q)install -Dm 0644 build/changelog.Debian.gz "${DEST_DIR}${DOC_DIR}"/ledger/changelog.Debian.gz
	$(Q)install -Dm 0644 build/copyright "${DEST_DIR}${DOC_DIR}"/ledger/copyright

	$(Q)install -Dm 0644 ledger/ledger/static/images/logo.png "${DEST_DIR}${ICON_DIR}"/hicolor/512x512/apps/ledger.png
	$(Q)install -Dm 0644 build/conf/ledger.desktop "${DEST_DIR}${SHARE_DIR}"/applications/ledger.desktop
	$(Q)install -Dm 0644 ledger.service "${DEST_DIR}${SYSTEMD_DIR}"/ledger.service
	@echo "ledger install completed."


uninstall:
	$(Q)rm -r "${DEST_DIR}${SHARE_DIR}"/ledger
	$(Q)rm -r "${DEST_DIR}${DOC_DIR}"/ledger
	$(Q)rm "${DEST_DIR}${ICON_DIR}"/hicolor/512x512/apps/ledger.png
	$(Q)rm "${DEST_DIR}${SHARE_DIR}"/applications/ledger.desktop
	$(Q)rm "${DEST_DIR}${SYSTEMD_DIR}"/ledger.service
	@echo "ledger uninstall completed."


build:
	$(Q)mkdir -p build


build/bin: build
	$(Q)mkdir -p build/bin


build/conf: build
	$(Q)mkdir -p build/conf


build/package/DEBIAN: build
	@mkdir -p build/package/DEBIAN


build/copyright: build
	$(Q)echo "Upstream-Name: ledger" > build/copyright
	$(Q)echo "Source: https://github.com/jnphilipp/ledger" >> build/copyright
	$(Q)echo "" >> build/copyright
	$(Q)echo "Files: *" >> build/copyright
	$(Q)echo "Copyright: 2014-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>" >> build/copyright
	$(Q)echo "License: GPL-3+" >> build/copyright
	$(Q)echo " This program is free software: you can redistribute it and/or modify" >> build/copyright
	$(Q)echo " it under the terms of the GNU General Public License as published by" >> build/copyright
	$(Q)echo " the Free Software Foundation, either version 3 of the License, or" >> build/copyright
	$(Q)echo " any later version." >> build/copyright
	$(Q)echo "" >> build/copyright
	$(Q)echo " This program is distributed in the hope that it will be useful," >> build/copyright
	$(Q)echo " but WITHOUT ANY WARRANTY; without even the implied warranty of" >> build/copyright
	$(Q)echo " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the" >> build/copyright
	$(Q)echo " GNU General Public License for more details." >> build/copyright
	$(Q)echo "" >> build/copyright
	$(Q)echo " You should have received a copy of the GNU General Public License" >> build/copyright
	$(Q)echo " along with this program. If not, see <http://www.gnu.org/licenses/>." >> build/copyright
	$(Q)echo " On Debian systems, the full text of the GNU General Public" >> build/copyright
	$(Q)echo " License version 3 can be found in the file" >> build/copyright
	$(Q)echo " '/usr/share/common-licenses/GPL-3'." >> build/copyright


build/changelog.Debian.gz: build
	$(Q)declare TAGS=(`git tag --sort=creatordate`); for ((i=$${#TAGS[@]};i>=0;i--)); do if [ $$i -eq 0 ]; then git log $${TAGS[$$i]} --no-merges --format="ledger ($${TAGS[$$i]}-%h) unstable; urgency=medium%n%n  * %s%n    %b%n -- %an <%ae>  %aD%n" | sed "/^\s*$$/d" >> build/changelog; elif [ $$i -eq $${#TAGS[@]} ]; then git log $${TAGS[$$i-1]}..HEAD --no-merges --format="ledger ($${TAGS[$$i-1]}-%h) unstable; urgency=medium%n%n  * %s%n    %b%n -- %an <%ae>  %aD%n" | sed "/^\s*$$/d" >> build/changelog; else git log $${TAGS[$$i-1]}..$${TAGS[$$i]} --no-merges --format="ledger ($${TAGS[$$i]}-%h) unstable; urgency=medium%n%n  * %s%n    %b%n -- %an <%ae>  %aD%n" | sed "/^\s*$$/d" >> build/changelog; fi; done
	$(Q)cat build/changelog | gzip -n9 > build/changelog.Debian.gz


changelog.latest.md:
	$(Q)( \
		declare TAGS=(`git tag --sort=creatordate`); \
		for ((i=$${#TAGS[@]};i>=0;i--)); do \
			if [ $$i -eq 0 ]; then \
				echo -e "$${TAGS[$$i]}" >> changelog.latest.md; \
				git log $${TAGS[$$i]} --no-merges --format="  * %h %s"  >> changelog.latest.md; \
			elif [ $$i -eq $${#TAGS[@]} ] && [ $$(git log $${TAGS[$$i-1]}..HEAD --oneline | wc -l) -ne 0 ]; then \
				echo -e "$${TAGS[$$i-1]}-$$(git log -n 1 --format='%h')" >> changelog.latest.md; \
				git log $${TAGS[$$i-1]}..HEAD --no-merges --format="  * %h %s"  >> changelog.latest.md; \
			elif [ $$i -lt $${#TAGS[@]} ]; then \
				echo -e "$${TAGS[$$i]}" >> changelog.latest.md; \
				git log $${TAGS[$$i-1]}..$${TAGS[$$i]} --no-merges --format="  * %h %s"  >> changelog.latest.md; \
				break; \
			fi; \
		done \
	)


build/conf/ledger.desktop: build/conf
	@echo "[Desktop Entry]" > build/conf/ledger.desktop
	@echo "Version=1.0" >> build/conf/ledger.desktop
	@echo "Categories=Network;Finance;" >> build/conf/ledger.desktop
	@echo "Icon=ledger" >> build/conf/ledger.desktop
	@echo "Name=ledger" >> build/conf/ledger.desktop
	@echo "Exec=xdg-open http://localhost:8080" >> build/conf/ledger.desktop
	@echo "Terminal=false" >> build/conf/ledger.desktop
	@echo "Type=Application" >> build/conf/ledger.desktop
	@echo "StartupNotify=true" >> build/conf/ledger.desktop
	@echo "OnlyShowIn=GNOME;" >> build/conf/ledger.desktop
	@echo "Keywords=Ledger" >> build/conf/ledger.desktop
	@echo "Name[en_US]=ledger" >> build/conf/ledger.desktop
	@echo "Name[de_DE]=Haushaltsbuch" >> build/conf/ledger.desktop


build/package/DEBIAN/md5sums:
	$(Q)make install DEST_DIR=build/package
	$(Q)mkdir -p build/package/DEBIAN
	$(Q)find build/package -type f -not -path "*DEBIAN*" -exec md5sum {} \; > build/md5sums
	$(Q)sed -e "s/build\/package\///" build/md5sums > build/package/DEBIAN/md5sums
	$(Q)chmod 0644 build/package/DEBIAN/md5sums


build/package/DEBIAN/control: build/package/DEBIAN/md5sums
	$(Q)echo "Package: ledger" > build/package/DEBIAN/control
	$(Q)echo "Version: `git describe --tags`-`git log --format=%h -1`" >> build/package/DEBIAN/control
	$(Q)echo "Section: utils" >> build/package/DEBIAN/control
	$(Q)echo "Priority: optional" >> build/package/DEBIAN/control
	$(Q)echo "Architecture: all" >> build/package/DEBIAN/control
	$(Q)echo "Depends: python3 (<< 3.11), python3 (>= 3.7), python3:any, python3-gi:any, python3-django (= 4.0~), python3-dateutil (=2.8~)" >> build/package/DEBIAN/control
	$(Q)echo "Recommends: systemd" >> build/package/DEBIAN/control
	$(Q)echo "Installed-Size: `du -sk build/package/usr | grep -oE "[0-9]+"`" >> build/package/DEBIAN/control
	$(Q)echo "Maintainer: J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>" >> build/package/DEBIAN/control
	$(Q)echo "Homepage: https://github.com/jnphilipp/ledger" >> build/package/DEBIAN/control
	$(Q)echo "Description: Web based ledger system to keep track of your money" >> build/package/DEBIAN/control
	$(Q)echo " This tool provides a website to keep track of accounts and their entries. It" >> build/package/DEBIAN/control
	$(Q)echo " provides a budget overview and detailed statistics ans has the option to" >> build/package/DEBIAN/control
	$(Q)echo " upload invoices, statements, etc. and attachem thos the appropriate" >> build/package/DEBIAN/control
	$(Q)echo " account/entry. Runs as a systemd service." >> build/package/DEBIAN/control
