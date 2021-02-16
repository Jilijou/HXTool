#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import hashlib
try:
	from pandas import DataFrame
except ImportError:
	print("hxtool_data_models requires the 'pandas' module, please install it.")
	exit(1)

class hxtool_data_models:
	def __init__(self, stack_type):
		self.stack_type = self.stack_types[stack_type]
	
	def stack_data(self, data, index = None, group_by = None):
		if len(data) > 0:
	
			if not index:
				index = self.stack_type['default_index']
			if not group_by:
				group_by = self.stack_type['default_groupby']
 
			try:
				data_frame = DataFrame(data).astype(unicode)
			except NameError:
				# under Python 3, str is unicode
				data_frame = DataFrame(data).astype(str)
 
			data_frame.replace('nan', '', inplace = True)
			
			# Drop duplicates
			duplicate_filter = [index]
			duplicate_filter.extend(group_by)
			data_frame.drop_duplicates(subset = duplicate_filter, inplace = True)
			
			data_frame = data_frame.groupby(by = group_by).apply(lambda _: list(_[index])).reset_index(name = index)
			data_frame['count'] = data_frame[index].apply(lambda _: len(_))
			data_frame.sort_values(by = 'count', ascending = False, inplace = True)
			return data_frame.to_json(orient = 'records')
		else:
			return '{}'
	
	def w32mbr_post_process(mbr_data):
		return {
				'Md5sum' : hashlib.md5(mbr_data).hexdigest(),
				'Sha1sum' : hashlib.sha1(mbr_data).hexdigest(),
				'Sha256sum' : hashlib.sha256(mbr_data).hexdigest()
				}
		
	stack_types = {
		"all-ports": {
			"audit_module" : "ports",
			"script": "ports.json",
			"platform": "all",
			"name" : "Ports",
			"item_name": "PortItem",
			"fields": [
				"remotePort",
				"protocol",
				"localPort",
				"process",
				"pid",
				"localIP",
				"state",
				"remoteIP",
				"path"
			],
			"default_index": "hostname",
			"default_groupby": ['path', 'localIP', 'localPort', 'state', 'remoteIP', 'remotePort'],			
			"post_process": None
		},
		"all-processes-api": {
			"audit_module" : "processes-api",
			"script" : "processes-api.json",
			"platform" : "all",
			"name" : "Process",
			"item_name" : "ProcessItem",
			"fields" : [
				"Username",
				"SectionList",
				"name",
				"parentpid",
				"PortList",
				"HandleList",
				"pid",
				"SecurityType",
				"kernelTime",
				"SecurityID",
				"arguments",
				"startTime",
				"path",
				"userTime"
				],
			"default_index" : "hostname",
			"default_groupby" : ["name", "path", "arguments"],			
			"post_process" : None
		},
		"windows-services": {
			"audit_module" : "w32services",
			"script": "services-md5.xml",
			"platform": "windows",
			"name" : "Services MD5",
			"item_name": "ServiceItem",
			"fields": [
				"name",
				"descriptiveName",
				"description",
				"mode",
				"startedAs",
				"path",
				"pathmd5sum",
				"arguments",
				"serviceDLL",
				"serviceDLLmd5sum",
				"status",
				"pid",
				"type"
				],
			"default_index": "hostname",
			"default_groupby": ["name", "path", "pathmd5sum", "serviceDLL", "serviceDLLmd5sum"],
			"post_process": None
		},
		"windows-drivermodules": {
			"audit_module" : "w32drivers-modulelist",
			"script" : "w32drivers-modulelist.xml",
			"platform" : "windows",
			"name" : "Driver Modules",
			"item_name" : "ModuleItem",
			"fields" : [
				"ModuleName",
				"ModuleInit",
				"ModuleAddress",
				"ModuleSize",
				"ModuleBase",
				"ModulePath",
			],
			"default_index" : "hostname",
			"default_groupby" : ["ModuleName", "ModuleSize", "ModulePath"],
			"post_process" : None
		},
		"windows-driversignature": {
			"audit_module" : "w32drivers-signature",
			"script" : "w32drivers-signature.xml",
			"platform" : "windows",
			"name" : "Driver Signature",
			"item_name" : "DriverItem",
			"fields" : [
				"ImageSize",
				"DriverObjectAddress",
				"DriverName",
				"DriverUnload",
				"Sha256sum",
				"DeviceItem",
				"Md5sum",
				"PEInfo",
				"DriverStartIo",
				"DriverInit",
				"ImageBase",
				"Sha1sum",
			],
			"default_index" : "hostname",
			"default_groupby" : ["DriverName", "Md5sum", "Sha1sum"],
			"post_process" : None
			
		},
		"windows-processes-memory": {
			"audit_module" : "w32processes-memory",
			"script" : "w32processes-memory.xml",
			"platform" : "windows",
			"name" : "Process",
			"item_name" : "ProcessItem",
			"fields" : [
				"Username",
				"SectionList",
				"name",
				"parentpid",
				"PortList",
				"HandleList",
				"pid",
				"SecurityType",
				"kernelTime",
				"SecurityID",
				"arguments",
				"startTime",
				"path",
				"userTime"
				],
			"default_index" : "hostname",
			"default_groupby" : ["name", "path", "arguments"],			
			"post_process" : None
		},
		"windows-tasks": {
			"audit_module" : "w32tasks",
			"script": "w32tasks.xml",
			"platform": "windows",
			"name" : "Task",
			"item_name": "TaskItem",
			"fields": [
				"Status",
				"Name",
				"Creator",
				"MaxRunTime",
				"AccountName", 
				"AccountLogonType", 
				"MostRecentRunTime", 
				"Flag", 
				"AccountRunLevel", 
				"NextRunTime", 
				"ActionList", 
				"TriggerList", 
				"VirtualPath", 
				"ExitCode", 
				"CreationDate", 
				"Comment"
				],
			"default_index": "hostname",
			"default_groupby": ["Name", "Creator", "AccountLogonType", "ActionList"],
			"post_process": None
		},
		"windows-mbr" : {
			"audit_module" : "w32disk-acquisition",
			"script" : "w32mbr.xml",
			"platform" : "windows",
			"name" : "Master Boot Record",
			"item_name" : "",
			"fields" : [],
			"default_index" : "hostname",
			"default_groupby" : ["Md5sum", "Sha1sum", "Sha256sum"],
			"post_process" : w32mbr_post_process
		}
	}
	
