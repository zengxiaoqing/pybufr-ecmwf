#!/usr/bin/env python

# Copyright J. de Kloe
# This software is licensed under the terms of the LGPLv3 Licence
# which can be obtained from https://www.gnu.org/licenses/lgpl.html

import os          # operating system functions
import urllib      # handling of url downloads
import re          # handling of regular expressions
from HTMLParser import HTMLParser # parsing of html

old = False
#old = True

class MyHtmlParser(HTMLParser):
    #  #[ a custom parser class to parse the html
    def __init__(self,*args,**kwargs):
	HTMLParser.__init__(self,*args,**kwargs)
	self.bufr_lib_versions = []
    def handle_starttag(self, tag, attrs):
	d = dict(attrs)
	if tag=='a':
	    if d.get('class') == 'filename':
		bufr_tarfile_name = d.get('data-filename')
		bufr_lib_url      = d.get('href')
		print('a found; tarfile = ', bufr_tarfile_name,
		      'href = ', bufr_lib_url)
		self.bufr_lib_versions.append((bufr_tarfile_name,bufr_lib_url))
    #  #]

def find_newest_library(verbose=False):
    if old:
	#  #[ retrieve from old website
	URL_ECMWF_WEBSITE = "http://old.ecmwf.int/"
	URL_BUFR_PAGE = URL_ECMWF_WEBSITE+"products/data/"+\
			"software/download/bufr.html"
	line_pattern = r'<TD .*><A HREF="(.*)" .*>(.*)</A>(.*)</TD>'
	
	bufr_lib_versions = []
	urlf = urllib.urlopen(URL_BUFR_PAGE)
	lines = urlf.readlines()
	urlf.close()
	
	for line in lines:
	    if ".tar.gz" in line:
		match_object = re.match(line_pattern, line)
		if match_object:
		    data = match_object.groups()
		    if verbose:
			print(data)
		    bufr_lib_versions.append(data)

	# find most recent library version, for now just sort on name
	# that should do the trick
	most_recent_bufr_lib_url = ""
	most_recent_bufr_tarfile_name = ""
	# most_recent_bufr_lib_date = ""

	# example values for data:
	# data[0] = '/products/data/software/download/software_files/'+\
	#           'bufr_000380.tar.gz'
	# data[1] = 'bufr_000380.tar.gz'
	# data[2] = ' 28.07.2009'
	for data in bufr_lib_versions:
	    bufr_lib_url = data[0]
	    bufr_tarfile_name = data[1]
	    # bufr_lib_date = data[2]
	    if bufr_tarfile_name > most_recent_bufr_tarfile_name:
		# store
		most_recent_bufr_lib_url = bufr_lib_url
		most_recent_bufr_tarfile_name = bufr_tarfile_name
		# most_recent_bufr_lib_date = bufr_lib_date

	# report the result
	return (URL_ECMWF_WEBSITE+most_recent_bufr_lib_url,
		most_recent_bufr_tarfile_name)
	#  #]
    else: # new: 
	#  #[ retrieve from new website
	URL_ECMWF_WEBSITE = "https://software.ecmwf.int/"
	URL_BUFR_PAGE = URL_ECMWF_WEBSITE+"wiki/display/BUFR/Releases"
	
	urlf = urllib.urlopen(URL_BUFR_PAGE)
	html = urlf.read()
	urlf.close()
	
	parser = MyHtmlParser()
	parser.feed(html)

	parser.bufr_lib_versions.sort()

	( most_recent_bufr_tarfile_name,
	  most_recent_bufr_lib_url      ) = parser.bufr_lib_versions[-1]
	
	return (URL_ECMWF_WEBSITE+most_recent_bufr_lib_url,
		most_recent_bufr_tarfile_name)
	#  #]

def download_bufrlib_sources(download_url, ecmwf_bufr_lib_dir,
			     bufr_tarfile_name, verbose=False):
        #  #[ download the source tar file
        """ a method to download the most recent version of the
        ECMWF BUFR library tarball from the ECMWF website """
	
        if verbose:
            print("trying to download: ", most_recent_bufr_tarfile_name)

        try:
            # Get a file-like object for this website
            urlf = urllib.urlopen(download_url)
        except IOError:
            print("connection failed......")
            print("could not open url: ", download_url)
            return False

        tarfiledata = urlf.read()
        urlf.close()
        if verbose:
            print("ECMWF library downloaded successfully")

        local_fullname = os.path.join(ecmwf_bufr_lib_dir,
                                      bufr_tarfile_name)
        tfd = open(local_fullname, 'wb')
        tfd.write(tarfiledata)
        tfd.close()

        if verbose:
            print("stored in file: ", bufr_tarfile_name)

        return True
        #  #]

if __name__ == '__main__':
    (most_recent_bufr_lib_url,
     most_recent_bufr_tarfile_name) = find_newest_library(verbose=True)
    print("Most recent library version seems to be: ",
	  most_recent_bufr_tarfile_name)
    print("and can be downloaded from this url: ",
	  most_recent_bufr_lib_url)
    download_dir = './'
    download_bufrlib_sources(most_recent_bufr_lib_url, download_dir,
                             most_recent_bufr_tarfile_name, verbose=True)
