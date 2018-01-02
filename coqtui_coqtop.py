import os
import re
import subprocess
import xml.etree.ElementTree as ET
import signal

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
        self.response = ''
    def to_string(self):
        xml = ET.Element('call', {'val': self.tag})
        self.build_xml(xml)
        return ET.tostring(xml, 'utf-8')
    def receive(self, string):
        self.response = self.response + string
        try:
            elt = ET.fromstring('<coqtoproot>' + fix(self.response) + '</coqtoproot>')
            for c in elt:
                if c.tag == 'value':
                    self.parse_response(elt)
                    return True
        except ET.ParseError as e:
            return False

    def build_xml(self, xml):
        xml.extend([ET.Element('unit')])
    def parse_response(self, xml):
        pass
        
class CmdAbout(Cmd):
    def __init__(self):
        Cmd.__init__(self, 'About')
    def build_xml(self, xml):
        unit = ET.Element('unit')
        xml.extend([unit])
    def parse_response(self, xml):
        print [x.text for x in xml.findall('./value/coq_info/string')]

class CmdGoal(Cmd):
    def __init__(self):
        Cmd.__init__(self, 'Goal')
    def build_xml(self, xml):
        unit = ET.Element('unit')
        xml.extend([unit])
    def parse_response(self, xml):
        pass   

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
            , preexec_fn = ignore_sigint
            )
        self.logger = logger
        if self.logger is None:
            self.logger = EmptyLogger()

    def start_cmd(self, cmd):
        if self.current_cmd is not None:
            raise Exception("CMD not finished")
        self.current_cmd = cmd
        string = cmd.to_string()
        self.logger.log("---- SEND BEGIN ----\n" + string + "\n---- SEND END ----\n")
        self.coqtop.stdin.write(string)
        self.coqtop.stdin.flush()

    def finish_cmd(self):
        if self.current_cmd is None:
            return None
        fd = self.coqtop.stdout.fileno()
        d = os.read(fd, 0x4000)
        self.logger.log("---- RECV BEGIN ----\n" + d + "\n---- RECV END ----\n")
        finished = self.current_cmd.receive(d)
        if finished:
            cmd = self.current_cmd
            self.current_cmd = None
            return cmd
        else:
            return None

if __name__ == "__main__":
    coqtop = Coqtop(DebugLogger(), [])
    cmd = CmdAbout()
    coqtop.start_cmd(cmd)
    while True:
        cmd = coqtop.finish_cmd()
        if cmd is None:
            continue
        break
    coqtop.start_cmd(CmdGoal())
    while True:
        cmd = coqtop.finish_cmd()
        if cmd is None:
            continue
        break

