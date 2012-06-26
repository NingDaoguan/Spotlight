programName = spotlight-8
version=`date +%Y.%m.%d`

default:
	echo "try 'make clean', 'make install', 'make mac' or 'make rpm'"

clean:
	rm -rf *.py?  .#* *~ *.tar.gz *.tgz *.rpm *.txt MANIFEST AviTransferFile build dist *.app *.dmg

manifest: clean
	find  . -name '.' -o -name 'MANIFEST' -o -name 'CVS*' -prune  -o -type d  -o -print > MANIFEST

install: manifest
	mkdir -p $(ROOT)/usr/local/lib/${programName}
	(tar cf - -T MANIFEST) | (cd $(ROOT)/usr/local/lib/${programName}; tar xf - )
	rm -rf $(ROOT)/usr/local/bin/${programName}
	mkdir -p $(ROOT)/usr/local/bin
	ln -s ../lib/${programName}/SpotlightStart.py $(ROOT)/usr/local/bin/${programName}
	rm -rf MANIFEST

tarball: manifest
	tar zcvf ${programName}-${version}.tar.gz -T MANIFEST
	rm -rf MANIFEST

rpm: tarball
	rpmbuild -ta ${programName}-${version}.tar.gz > output
	output=`(cat output | grep 'Wrote:' | cut -d' ' -f2)`;\
	for i in $$output;do\
		mv $$i .;\
	done
	rm -rf output

mac: tarball
	python setup.py py2app -p wx,wxPython
	mv dist/Spotlight-8.app .
	rm -rf build dist
	hdiutil create -attach -fs HFS+ -size 30m -volname Spotlight-8 Spotlight-8
	cp -R Spotlight-8.app /Volumes/Spotlight-8
	mv Spotlight-8-${version}.tar.gz /Volumes/Spotlight-8
	cp -R DemoImages /Volumes/Spotlight-8
	rm -rf /Volumes/Spotlight-8/DemoImages/CVS
	echo 'To install, copy Spotlight-8 to your Applications folder.' >  /Volumes/Spotlight-8/readme.txt
	echo 'The .tar.gz file is the source code for programmers.' >> /Volumes/Spotlight-8/readme.txt
	echo 'The DemoImages folder contains example images as seen in the manual.' >> /Volumes/Spotlight-8/readme.txt
	echo 'The manual is available from the "Help->View Documentation" menu.' >> /Volumes/Spotlight-8/readme.txt
	hdiutil detach /Volumes/Spotlight-8
	hdiutil convert -format UDZO Spotlight-8.dmg -o Spotlight-8-${version}.dmg
	rm -f Spotlight-8.dmg
