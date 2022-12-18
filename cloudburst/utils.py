import json
import requests
from pathlib import Path
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from tqdm.contrib.concurrent import thread_map, process_map

def download(url, filename):
	with open(filename, "wb") as f:
		try:
			f.write(requests.get(url).content)
		except Exception as e:
			print(f"\033[31mError occured during download of content at \033[4m{url}\033[31m\n{e}\033[0m")

def download_tuple(tuple):
	download(tuple[0], tuple[1])

def concurrent(func,
				 input_list,
				 executor="threadpool",
				 progress_bar=False,
				 desc=""):
	# Get CPU count to use for max workers
	max_workers_count = multiprocessing.cpu_count() - 2
	# MultiThreading
	if executor == "threadpool":
		if progress_bar == False:
			results = []
			with ThreadPoolExecutor(max_workers=max_workers_count) as executor:
				futures = {executor.submit(func, i): i for i in input_list}
				for future in as_completed(futures):
					val = futures[future]
					try:
						data = future.result()
						results.append(data)
					except Exception as exc:
						print("{} generated an exception: {}".format(val, exc))
			return results
		else:
			return thread_map(func,
								input_list,
								max_workers=max_workers_count,
								desc=desc)
	# MultiProcessing
	elif executor == "processpool":
		if progress_bar == False:
			results = []
			with ProcessPoolExecutor(
					max_workers=max_workers_count) as executor:
				futures = {executor.submit(func, i): i for i in input_list}
				for future in as_completed(futures):
					val = futures[future]
					try:
						data = future.result()
						results.append(data)
					except Exception as exc:
						print("{} generated an exception: {}".format(val, exc))
			return results
		else:
			return process_map(func,
								 input_list,
								 max_workers=max_workers_count,
								 desc=desc)
	# Invalid executor given
	else:
		raise Exception(
			'Error: please use executor "processpool" (default) or "threadpool"'
		)

def mkdir(dirname):
	dirpath = Path.cwd().joinpath(dirname)
	if not dirpath.exists():
		dirpath.mkdir()
	return dirpath

def write_dict_to_file(filename, input_dict, minimize=False):
	with open(filename, "w") as f:
		if minimize:
			f.write(json.dumps(input_dict, separators=(",", ":")))
		else:
			f.write(json.dumps(input_dict, indent=4))


def get_dict_from_file(filename):
	try:
		with open(filename) as f:
			return json.load(f)
	except:
		return None
