#!/usr/bin/python

import argparse
import json
import sys
import distutils.util

# update info
current_script_version = 4
version_info_url = "http://localhost/~username/latest_script_version.txt" # only returns a version number
download_url = "http://localhost/~username/" # gives a user info to download and install
minimum_update_check_duration_in_seconds = 60 * 60 * 24 # once a day

# html insertions
insert_at_head_start = """
<!-- some stuff at head start 1 -->
<!-- some stuff at head start 2 -->
"""

insert_at_head_end = """
<!-- some stuff at head end 1 -->
<!-- some stuff at head end 2 -->
"""

insert_at_body_start = """
<!-- some stuff at body start 1 -->
<!-- some stuff at body start 2 -->
"""

insert_at_body_end = """
<!-- some stuff at body end 1 -->
<!-- some stuff at body end 2 -->
"""


class HypeURLType:
	Unknown = 0
	HypeJS = 1
	Resource = 2
	Link = 3
	ResourcesFolder = 4

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--get_options', action='store_true')
	parser.add_argument('--get_file_extension', action='store_true')
	parser.add_argument('--replace_url')
	parser.add_argument('--url_type')
	parser.add_argument('--is_reference', default="False")
	parser.add_argument('--modify_staging_path')
	parser.add_argument('--destination_path')
	parser.add_argument('--is_preview', default="False")
	parser.add_argument('--check_for_updates', action='store_true')
	args = parser.parse_args()
	
	
	## --get_file_extension
	##		return a dictionary of options
	if args.get_options:
		options = {}
		options['exportShouldInlineHypeJS'] = False
		options['exportShouldInlineDocumentLoader'] = False
		options['exportShouldUseExternalRuntime'] = False
		#options['exportExternalRuntimeURL'] = "";
		options['exportShouldSaveHTMLFile'] = True
		options['exportShouldNameAsIndexDotHTML'] = True
		#options['indexTitle'] = ""
		options['exportShouldBustBrowserCaching'] = False
		options['exportShouldIncludeTextContents'] = False
		options['exportShouldIncludePIE'] = True
		options['exportSupportInternetExplorer6789'] = True
		#options['initialSceneIndex'] = 0
		
		print json.dumps({"result" : options})
		sys.exit(0)


	## --get_file_extension
	##		return a string
	elif args.get_file_extension:
		print json.dumps({"result" : "zip"})
		sys.exit(0)


	## --replace_url [url] --url_type [HypeURLType] --is_reference [True|False]
	##		return a dictionary with "url" and "is_reference" keys
	##		if HypeURLType.ResourcesFolder, you can set the url to "." so there is no .hyperesources folder and everything
	##		is placed nex to the .html file
	elif args.replace_url != None:
		url_info = {}
		url_info['is_reference'] = bool(distutils.util.strtobool(args.is_reference))
		
		if int(args.url_type) == HypeURLType.ResourcesFolder:
			url_info['url'] = "."
			pass
		elif (int(args.url_type) == HypeURLType.HypeJS):
			url_info['url'] = "js/" + args.replace_url
		elif (int(args.url_type) == HypeURLType.Resource):
			if args.replace_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.psd', '.pdf')):
				url_info['url'] = "img/" + args.replace_url
			else:
				url_info['url'] = "misc/" + args.replace_url

		else:
			url_info['url'] = args.replace_url
		

		print json.dumps({"result" : url_info})
		sys.exit(0)


	## --modify_staging_path [filepath] --destination_path [filepath] --is_preview [True|False]
	##		return True if you moved successfully to the destination_path, otherwise don't return anything and Hype will make the move
	##		make any changes you'd like before the save is complete
	##		for example, if you are a zip, you need to zip and write to the destination_path
	##		or you may want to inject items into the HTML file
	##		if it is a preview, you shouldn't do things like zip it up, as Hype needs to know where the index.html file is
	elif args.modify_staging_path != None:
		import os
		is_preview = bool(distutils.util.strtobool(args.is_preview))
		
		index_path = os.path.join(args.modify_staging_path, "index.html")
		perform_html_additions(index_path)

		if is_preview == True:
			import shutil
			shutil.move(args.modify_staging_path, args.destination_path)
			print json.dumps({"result" : True})
		else:
			zip(args.modify_staging_path, args.destination_path)
			print json.dumps({"result" : True})
		sys.exit(0)

	## --check_for_updates
	##		return a dictionary with "url", "from_version", and "to_version" keys if there is an update, otherwise don't return anything and exit
	##		it is your responsibility to decide how often to check
	elif args.check_for_updates:
		import subprocess
		import urllib2
		
		last_check_timestamp = None
		try:
			last_check_timestamp = subprocess.check_output(["defaults", "read", "com.tumult.SampleExportScript", "last_check_timestamp"]).strip()
		except:
			pass

		try:
			timestamp_now = subprocess.check_output(["date", "+%s"]).strip()
			if (last_check_timestamp == None) or ((int(timestamp_now) - int(last_check_timestamp)) > minimum_update_check_duration_in_seconds):
				subprocess.check_output(["defaults", "write", "com.tumult.SampleExportScript", "last_check_timestamp", timestamp_now])
				latest_script_version = int(urllib2.urlopen(version_info_url).read().strip())
				if latest_script_version > current_script_version:
					print json.dumps({"result" : {"url" : download_url, "from_version" : str(current_script_version), "to_version" : str(latest_script_version)}})
		except:
			pass

		sys.exit(0)


# HTML FILE MODIFICATION

def perform_html_additions(index_path):
	index_contents = None
	with open(index_path, 'r') as target_file:
		index_contents = target_file.read()
		
	if index_contents == None:
		return
		
	import re
	if insert_at_head_start != None:
		head_start = re.search("<head.*?>", index_contents, re.IGNORECASE).end()
		index_contents = index_contents[:head_start] + insert_at_head_start + index_contents[head_start:]
	if insert_at_head_end != None:
		head_end = re.search("</head", index_contents, re.IGNORECASE).start()
		index_contents = index_contents[:head_end] + insert_at_head_end + index_contents[head_end:]
	if insert_at_body_start != None:
		body_start = re.search("<body.*?>", index_contents, re.IGNORECASE).end()
		index_contents = index_contents[:body_start] + insert_at_body_start + index_contents[body_start:]
	if insert_at_body_end != None:
		body_end = re.search("</body", index_contents, re.IGNORECASE).start()
		index_contents = index_contents[:body_end] + insert_at_body_end + index_contents[body_end:]

	with open(index_path, 'w') as target_file:
		target_file.write(index_contents)



# UTILITIES

# from http://stackoverflow.com/questions/14568647/create-zip-in-python
def zip(src, dst):
	import os
	import zipfile
	zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
	abs_src = os.path.abspath(src)
	for dirname, subdirs, files in os.walk(src):
		for filename in files:
			absname = os.path.abspath(os.path.join(dirname, filename))
			arcname = absname[len(abs_src) + 1:]
			zf.write(absname, arcname)
	zf.close()


if __name__ == "__main__":
	main()