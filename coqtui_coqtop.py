import os
import re
import select
import subprocess
import xml.etree.ElementTree as ET
import signal
from collections import deque

class EmptyLogger:
    def log(self, message):
        pass
class DebugLogger:
    def log(self, message):
        print message

# there's only 5 escape in xml. coqtop use &nbsp;, which is
# incorrect. Fix it.
def fix(cmd):
    return cmd.replace("&nbsp;", ' ')

def ignore_sigint():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

class Cmd:
    def __init__(self, tag):
        self.tag = tag
    def to_string(self):
        xml = ET.Element('call', {'val': self.tag})
        self.build_xml(xml)
        return ET.tostring(xml, 'utf-8')
    def build_xml(self, xml):
        xml.extend([ET.Element('unit')])
    def parse_response(self, value_xml, all_xml):
        pass
 
class QueueCmd:
    def __init__(self):
        self.cmds = deque()
        self.response = ''
    def queue(self, cmd):
        self.cmds.append(cmd)
    def receive(self, data):
        self.response += data
        try:
            elt = ET.fromstring('<coqtoproot>'
                                + fix(self.response)
                                + '</coqtoproot>')
            for c in elt:
                if c.tag == 'value':
                    self.cmds[0].parse_response(c, elt)
                    self.cmds.popleft()
                    self.response = ''
        except ET.ParseError as e:
            return
    def is_empty(self):
        return len(self.cmds) == 0

class CmdAbout(Cmd):
    def __init__(self):
        Cmd.__init__(self, 'About')
    def build_xml(self, xml):
        unit = ET.Element('unit')
        xml.extend([unit])
    def parse_response(self, value_xml, all_xml):
        print [x.text for x in value_xml.findall('./coq_info/string')]

class CmdGoal(Cmd):
    def __init__(self):
        Cmd.__init__(self, 'Goal')
    def build_xml(self, xml):
        unit = ET.Element('unit')
        xml.extend([unit])
    def parse_response(self, value_xml, all_xml):
        print "parse_response: " + ET.tostring(value_xml)

class Coqtop:
    coqtop = None
    current_cmd = None
    recv_data = ''

    def __init__(self, logger, args):
        options = [ 'coqtop'
                  , '-ideslave'
                  , '-main-channel'
                  , 'stdfds'
                  , '-async-proofs'
                  , 'on'
                  ]

        # Exception should be catched outside
        self.coqtop = subprocess.Popen(
            options + list(args)
            , stdin = subprocess.PIPE
            , stdout = subprocess.PIPE
            , stderr = None
            , preexec_fn = ignore_sigint
            )
        self.logger = logger
        if self.logger is None:
            self.logger = EmptyLogger()
        self.cmds = QueueCmd()

    def queue_cmd(self, cmd):
        string = cmd.to_string()
        self.logger.log("---- SEND BEGIN ----\n" + string + "\n---- SEND END ----\n")
        self.coqtop.stdin.write(string)
        self.coqtop.stdin.flush()
        self.cmds.queue(cmd)

    def process(self):
        if self.cmds.is_empty():
            return
        fd = self.coqtop.stdout.fileno()

        if fd not in select.select([fd], [], [], 0)[0]:
            return None
        d = os.read(fd, 0x4000)
        self.logger.log("---- RECV BEGIN ----\n" + d + "\n---- RECV END ----\n")
        self.cmds.receive(d)

    def is_idle(self):
        return self.cmds.is_empty()

if __name__ == "__main__":
    coqtop = Coqtop(DebugLogger(), [])
    coqtop.queue_cmd(CmdAbout())
    coqtop.queue_cmd(CmdGoal())
    coqtop.queue_cmd(CmdGoal())
    coqtop.queue_cmd(CmdAbout())

    while not coqtop.is_idle():
        coqtop.process()
