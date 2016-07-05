from ci import models
import re

def set_job_modules(job, output):
  """
  The output has the following format:
    Currently Loaded Modulefiles:
      1) module1
      2) module2
      ...
    OR
    Currently Loaded Modules:
      1) module1
      2) module2
      ...
  """
  lines_match = re.search("(?<=^Currently Loaded Modulefiles:$)(\s+\d+\) (.*))+", output, flags=re.MULTILINE)
  if not lines_match:
    lines_match = re.search("(?<=^Currently Loaded Modules:$)(\s+\d+\) (.*))+", output, flags=re.MULTILINE)
    if not lines_match:
      mod_obj, created = models.LoadedModule.objects.get_or_create(name="None")
      job.loaded_modules.add(mod_obj)
      return

  modules = lines_match.group(0)
  # Assume that the module names don't have whitespace. Then "split" will have the module
  # names alternating with the "\d+)"
  mod_list = modules.split()[1::2]
  for mod in mod_list:
    mod_obj, created = models.LoadedModule.objects.get_or_create(name=mod)
    job.loaded_modules.add(mod_obj)

  if not mod_list:
    mod_obj, created = models.LoadedModule.objects.get_or_create(name="None")
    job.loaded_modules.add(mod_obj)

def output_os_search(job, output, name_re, version_re, other_re):
  """
  Search the output for OS information.
  If all the OS information is found then update the job with
  the appropiate record.
  Returns:
    bool: True if the job OS was set, otherwise False
  """
  os_name_match = re.search(name_re, output, flags=re.MULTILINE)
  if not os_name_match:
    return False

  os_name = os_name_match.group(1).strip()
  os_version_match = re.search(version_re, output, flags=re.MULTILINE)
  os_other_match = re.search(other_re, output, flags=re.MULTILINE)
  if os_version_match and os_other_match:
    os_version = os_version_match.group(1).strip()
    os_other = os_other_match.group(1).strip()
    os_record, created = models.OSVersion.objects.get_or_create(name=os_name, version=os_version, other=os_other)
    job.operating_system = os_record
    return True
  return False

def set_job_os(job, output):
  """
  Goes through a series of possible OSes.
  If no match was found then set the job OS to "Other"
  """
  # This matches against the output of "lsb_release -a".
  if output_os_search(job, output, "^Distributor ID:\s+(.+)$", "^Release:\s+(.+)$", "^Codename:\s+(.+)$"):
    return
  # This matches against the output of "systeminfo |grep '^OS'"
  if output_os_search(job, output, "^OS Name:\s+(.+)$", "^OS Version:\s+(.+)$", "^OS Configuration:\s+(.+)$"):
    return
  # This matches against the output of "sw_vers".
  if output_os_search(job, output, "^ProductName:\s+(.+)$", "^ProductVersion:\s+(.+)$", "^BuildVersion:\s+(.+)$"):
    return

  # No OS found
  os_record, created = models.OSVersion.objects.get_or_create(name="Other")
  job.operating_system = os_record

def set_job_info(job):
  """
  Sets the modules and OS of the job by scanning the output of
  the first StepResult for the job. It is assumed that all steps
  will have the same modules and OS.
  """
  step_result = job.step_results.first()
  if step_result:
    output = step_result.output
  else:
    output = ""

  job.loaded_modules.clear()
  job.operating_system = None
  set_job_modules(job, output)
  set_job_os(job, output)
  job.save()
