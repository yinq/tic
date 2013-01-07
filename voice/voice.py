#!/usr/bin/env python
import os, sys
import pexpect

RF_CMD = '/home/yinq/proj/tic/rf-control/dist/Debug/GNU_Arm-Linux-x86/rf24bb'

if __name__ == "__main__":
  os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'
  child = pexpect.spawn('pocketsphinx_continuous -adcdev hw:1,0')
  child.logfile = sys.stdout
  while True:
    try:
      child.expect(r'\d+: (.*)', timeout=None)
      cmd = child.match.group(1)
      if 'ight' in cmd:
        os.system('%s 1' % RF_CMD)
      elif cmd == 'off':
        os.system('%s 0' % RF_CMD)
      else:
        print 'Unrecognized command: %s' % cmd
    except KeyboardInterrupt:
      child.close(force=True)
      break

