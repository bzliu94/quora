# 2016-04-19

# made a predictive parser in accordance with rfc 3986

# we note that grammar is type-three

"""
FRAGMENTS
fragment ALPHA = [a-zA-Z]
fragment DIGIT = [0-9]
fragment HEXDIG = DIGIT | [a-fA-F]
fragment DEC_OCTET = DIGIT		; 0-9
		/ %x31-39 DIGIT		; 10-99
		/ "1" 2DIGIT		; 100-199
		/ "2" %x30-34 DIGIT	; 200-249
		/ "25" %x30-35		; 250-255
fragment IP_LITERAL = "[" ( IPV6ADDRESS / IPVFUTURE  ) "]"
fragment IPVFUTURE = "v" 1*HEXDIG "." 1*( UNRESERVED / SUB_DELIMS / ":" )
fragment IPV6ADDRESS = 		     6( H16 ":" ) LS32
		/			"::" 5( H16 ":" ) LS32
		/ [		  H16 ] "::" 4( H16 ":" ) LS32
		/ [ *1( H16 ":" ) H16 ] "::" 3( H16 ":" ) LS32
		/ [ *2( H16 ":" ) H16 ] "::" 2( H16 ":" ) LS32
		/ [ *3( H16 ":" ) H16 ] "::"	H16 ":"   LS32
		/ [ *4( H16 ":" ) H16 ] "::"		  LS32
		/ [ *5( H16 ":" ) H16 ] "::"		  H16
		/ [ *6( H16 ":" ) H16 ] "::"
fragment H16 = 1*4HEXDIG
fragment LS32 = ( H16 ":" H16 ) / IPV4ADDRESS
fragment IPV4ADDRESS = DEC_OCTET "." DEC_OCTET "." DEC_OCTET "." DEC_OCTET
fragment REG_NAME = *( UNRESERVED / PCT_ENCODED / SUB_DELIMS )
# path = path-abempty		; begins with "/" or is empty
#	/ path-absolute		; begins with "/" but not "//"
#	/ path-noscheme		; begins with a non-colon segment
#	/ path-rootless		; begins with a segment
#	/ path-empty		; zero characters
fragment PCHAR = UNRESERVED / PCT_ENCODED / SUB_DELIMS / ":" / "@"
fragment PCT_ENCODED = "%" HEXDIG HEXDIG
fragment UNRESERVED = ALPHA / DIGIT / "-" / "." / "_" / "~"
# RESERVED = GEN_DELIMS / SUB_DELIMS
# GEN_DELIMS = ":" / "/" / "?" / "#" / "[" / "]" / "@"
fragment SUB_DELIMS = "!" / "$" / "&" / "'" / "(" / ")"
			/ "*" / "+" / "," / ";" / "="
# remember that IPV4ADDRESS should have precedence over DIGIT
fragment HOST = IP_LITERAL / IPV4ADDRESS / REG_NAME
"""
"""
TOKEN RULES
care about prefix-wise relationships
gen. delimiters are safe anchors because we have O(1) of them, aside from '@' for segment-nz, ':' for userinfo, '/' for path
up to two-character look-behind with changing offset
narrow domains first
SEGMENT_NZ_NC = <'^'> 1*( UNRESERVED / PCT_ENCODED / SUB_DELIMS / "@" ) <'/|\?|#|$'>
		; non-zero-length segment without any colon ":"
SCHEME = <'^'> ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ) <':'>
USERINFO = <'//'> *( UNRESERVED / PCT_ENCODED / SUB_DELIMS / ":" ) <'@'>
HOST_WITH_PORT = <'(?://)|(?:.@)'> HOST ':' *DIGIT <'$|/'>
HOST_WITHOUT_PORT = <'(?://)|(?:.@)'> HOST <'$|/'>
SEGMENT_NZ = <':/'|'.:'> 1*PCHAR
SEGMENT = <'/'> *PCHAR
QUERY = <'?'> *( PCHAR / "/" / "?" )
FRAG = <'#'> *( PCHAR / "/" / "?" )
misc. tokens: '//', '/', ':', '?', '#', '@'
"""
"""
NON-TERMINAL RULES
uri_reference -> uri | relative_ref
# hier_part -> '//' authority path_abempty | path_absolute | path_rootless | path_empty
hier_part -> '//' authority path_abempty | path_absolute | path_rootless | EPSILON
uri -> SCHEME ':' hier_part uri_helper1
uri_helper1 -> uri_helper2 | '?' QUERY uri_helper2
uri_helper2 -> EPSILON | '#' FRAG
relative_ref -> relative_part uri_helper1
# relative_part -> '//' authority path_abempty | path_absolute | path_noscheme | path_empty
relative_part -> '//' authority path_abempty | path_absolute | path_noscheme | EPSILON
authority -> authority_helper1 authority_helper2
authority_helper1 -> EPSILON | USERINFO '@'
authority_helper2 -> HOST_WITH_PORT | HOST_WITHOUT_PORT
path_abempty -> EPSILON | '/' path_abempty_helper
path_abempty_helper -> SEGMENT path_abempty | path_abempty
path_absolute -> '/' path_absolute_helper1
path_absolute_helper1 -> EPSILON | SEGMENT_NZ path_absolute_helper2
path_absolute_helper2 -> EPSILON | '/' path_absolute_helper2b
path_absolute_helper2b -> SEGMENT_NZ path_absolute_helper2 | path_absolute_helper2
path_noscheme -> SEGMENT_NZ_NC path_noscheme_helper1
path_noscheme_helper1 -> EPSILON | '/' path_noscheme_helper1b
path_noscheme_helper1b -> path_noscheme_helper1 | SEGMENT path_noscheme_helper1
path_rootless -> SEGMENT_NZ path_rootless_helper1
path_rootless_helper1 -> EPSILON | '/' path_rootless_helper1b
path_rootless_helper1b -> path_rootless_helper1 | SEGMENT path_rootless_helper1
# epsilon is safe here, even though a lookahead was specified at rfc because FOLLOW(path_empty) is a specific kind of general delimiter that cannot appear at beginning of other path types ('?' or '#' or $)
# path_empty -> EPSILON
"""
import re
import sys
from collections import deque
import string
# TOKENS ENUMERATED
EPSILON = -1
SEGMENT_NZ_NC = 0
SCHEME = 1
USERINFO = 2
HOST_WITH_PORT = 3
HOST_WITHOUT_PORT = 4
SEGMENT_NZ = 5
SEGMENT = 6
QUERY = 7
FRAG = 8
EOF = -2
# FRAGMENT/TOKEN REGULAR EXPRESSIONS
ALPHA_FRAG_RE = r"[a-zA-Z]"
DIGIT_FRAG_RE = r"[0-9]"
HEXDIG_FRAG_RE = r"(?:(?:" + DIGIT_FRAG_RE + r")|(?:[a-fA-F]))"
SUB_DELIMS_FRAG_RE = r"[!$&'()*+,;=]"
UNRESERVED_FRAG_RE = r"(?:(?:" + ALPHA_FRAG_RE + r")|(?:" + DIGIT_FRAG_RE + r")|(?:[\-._~]))"
# have to be careful here; earlier rules within a regular expression string are preferred
DEC_OCTET_FRAG_RE = r"(?:(?:1" + DIGIT_FRAG_RE + DIGIT_FRAG_RE + r")|(?:2[0-4]" + DIGIT_FRAG_RE + r")|(?:25[0-5])|(?:[1-9]" + DIGIT_FRAG_RE + r")|(?:" + DIGIT_FRAG_RE + r"))"
IPV4ADDRESS_FRAG_RE = r"(?:" + DEC_OCTET_FRAG_RE + r"(?:\." + DEC_OCTET_FRAG_RE + r"){3})"
# made a mistake here; no space allowed in "{1,4}" modifier
H16_FRAG_RE = r"(?:(?:" + HEXDIG_FRAG_RE + r"){1,4})"
LS32_FRAG_RE = r"(?:(?:" + H16_FRAG_RE + r":" + H16_FRAG_RE + r")|(?:" + IPV4ADDRESS_FRAG_RE + r"))"
# made a mistake here; for items left of "::", have up to, say, four copies instead of exactly, say, four copies
# also, we forgot colons to left of "::"
IPV6ADDRESS_FRAG_RE1 = r"(?:(?:" + H16_FRAG_RE + r":){6}" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE2 = r"(?:\::(?:" + H16_FRAG_RE + r":){5}" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE3  = r"(?:(?:" + H16_FRAG_RE + r")?::(?:" + H16_FRAG_RE + r":){4}" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE4 = r"(?:(?:(?:" + H16_FRAG_RE + r":){0,1}" + H16_FRAG_RE + r")?::(?:" + H16_FRAG_RE + r":){3}" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE5  = r"(?:(?:(?:" + H16_FRAG_RE + r":){0,2}" + H16_FRAG_RE + r")?::(?:" + H16_FRAG_RE + r":){2}" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE6  = r"(?:(?:(?:" + H16_FRAG_RE + r":){0,3}" + H16_FRAG_RE + r")?::(?:" + H16_FRAG_RE + r":){1}" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE7  = r"(?:(?:(?:" + H16_FRAG_RE + r":){0,4}" + H16_FRAG_RE + r")?::" + LS32_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE8  = r"(?:(?:(?:" + H16_FRAG_RE + r":){0,5}" + H16_FRAG_RE + r")?::" + H16_FRAG_RE + r")"
IPV6ADDRESS_FRAG_RE9  = r"(?:(?:(?:" + H16_FRAG_RE + r":){0,6}" + H16_FRAG_RE + r")?::)"
IPV6ADDRESS_FRAG_RE = r"(?:(?:" + IPV6ADDRESS_FRAG_RE1 + r")|(?:" + IPV6ADDRESS_FRAG_RE2 + r")|(?:" + IPV6ADDRESS_FRAG_RE3 + r")|(?:" + IPV6ADDRESS_FRAG_RE4 + r")|(?:" + IPV6ADDRESS_FRAG_RE5 + r")|(?:" + IPV6ADDRESS_FRAG_RE6 + r")|(?:" + IPV6ADDRESS_FRAG_RE7 + r")|(?:" + IPV6ADDRESS_FRAG_RE8 + r")|(?:" + IPV6ADDRESS_FRAG_RE9 + r"))"
# made a mistake here; used in a different regular expression with "or", but didn't surround this with a pair of non-grouping parentheses
IPVFUTURE_FRAG_RE = r"(?:v(?:" + HEXDIG_FRAG_RE + r")+\.(?:" + UNRESERVED_FRAG_RE + r"|" + SUB_DELIMS_FRAG_RE + r"|:)+)"
# made a mistake here; "or" does not function as expected if we don't use non-matching parentheses around the choices
IP_LITERAL_FRAG_RE = r"(?:\[(?:(?:" + IPV6ADDRESS_FRAG_RE + r")|(?:" + IPVFUTURE_FRAG_RE + r"))\])"
PCT_ENCODED_FRAG_RE = r"(?:%" + HEXDIG_FRAG_RE + HEXDIG_FRAG_RE + r")"
REG_NAME_FRAG_RE = r"(?:(?:(?:" + UNRESERVED_FRAG_RE + r")|(?:" + PCT_ENCODED_FRAG_RE + r")|(?:" + SUB_DELIMS_FRAG_RE + r"))*)"
HOST_FRAG_RE = r"(?:(?:" + IP_LITERAL_FRAG_RE + r")|(?:" + IPV4ADDRESS_FRAG_RE + r")|(?:" + REG_NAME_FRAG_RE + r"))"
PCHAR_FRAG_RE = r"(?:(?:" + UNRESERVED_FRAG_RE + r")|(?:" + PCT_ENCODED_FRAG_RE + r")|(?:" + SUB_DELIMS_FRAG_RE + r")|[:@])"
SEGMENT_NZ_NC_BODY_RE = r"(?:(?:(?:" + UNRESERVED_FRAG_RE + r")|(?:" + PCT_ENCODED_FRAG_RE + r")|(?:" + SUB_DELIMS_FRAG_RE + r")|@)+)"
SCHEME_BODY_RE = r"(?:" + ALPHA_FRAG_RE + r"(?:" + ALPHA_FRAG_RE + r"|" + DIGIT_FRAG_RE + r"|[+\-.])*)"
USERINFO_BODY_RE = r"(?:(?:(?:" + UNRESERVED_FRAG_RE + r")|(?:" + PCT_ENCODED_FRAG_RE + r")|(?:" + SUB_DELIMS_FRAG_RE + r")|:)*)"
HOST_WITH_PORT_BODY_RE = r"(?:" + HOST_FRAG_RE + r":(?:(?:" + DIGIT_FRAG_RE + r")*))"
HOST_WITHOUT_PORT_BODY_RE = r"(?:" + HOST_FRAG_RE + r")"
SEGMENT_NZ_BODY_RE = r"(?:(?:" + PCHAR_FRAG_RE + r")+)"
# SEGMENT_BODY_RE = r"(?:(?:" + PCHAR_FRAG_RE + r")*)"
SEGMENT_BODY_RE = r"(?:(?:" + PCHAR_FRAG_RE + r")+)"
QUERY_BODY_RE = r"(?:(?:" + PCHAR_FRAG_RE + r"|/|\?)*)"
FRAG_BODY_RE = r"(?:(?:" + PCHAR_FRAG_RE + r"|/|\?)*)"
SEGMENT_NZ_NC_RE = r"(?:(?<=^)" + SEGMENT_NZ_NC_BODY_RE + r"(?=/|\?|#|$))"
SCHEME_RE = r"(?:(?<=^)" + SCHEME_BODY_RE + r"(?=\:))"
USERINFO_RE = r"(?:(?<=//)" + USERINFO_BODY_RE + r"(?=@))"
HOST_WITH_PORT_RE = r"(?:(?:(?<=//)|(?<=@))" + HOST_WITH_PORT_BODY_RE + r"(?=$|/))"
HOST_WITHOUT_PORT_RE = r"(?:(?:(?<=//)|(?<=@))" + HOST_WITHOUT_PORT_BODY_RE + r"(?=$|/))"
SEGMENT_NZ_RE = r"(?:(?:(?<=^/)|(?<=.:))" + SEGMENT_NZ_BODY_RE + r")"
SEGMENT_RE = r"(?:(?<=/)" + SEGMENT_BODY_RE + r")"
QUERY_RE = r"(?:(?<=\?)" + QUERY_BODY_RE + r")"
FRAG_RE = r"(?:(?<=\#)" + FRAG_BODY_RE + r")"
DOUBLE_FORWARD_SLASH_RE = r"(?://)"
SINGLE_FORWARD_SLASH_RE = r"/"
COLON_RE = r":"
QUESTION_MARK_RE = r"\?"
HASH_SIGN_RE = r"\#"
AT_SIGN_RE = r"@"
MISC_RE = r"(?:" + DOUBLE_FORWARD_SLASH_RE + r"|" + SINGLE_FORWARD_SLASH_RE + r"|" + COLON_RE + r"|" + QUESTION_MARK_RE + r"|" + HASH_SIGN_RE + r"|" + AT_SIGN_RE + r")"
OVERALL_RE = r"(?P<segment_nz_nc>" + SEGMENT_NZ_NC_RE + r")|(?P<scheme>" + SCHEME_RE + r")|(?P<userinfo>" + USERINFO_RE + r")|(?P<host_with_port>" + HOST_WITH_PORT_RE + r")|(?P<host_without_port>" + HOST_WITHOUT_PORT_RE + r")|(?P<segment_nz>" + SEGMENT_NZ_RE + r")|(?P<segment>" + SEGMENT_RE + r")|(?P<query>" + QUERY_RE + r")|(?P<frag>" + FRAG_RE + r")|(?P<misc>" + MISC_RE + r")"
# PARSER CLASSES
class ParseTree:
  def __init__(self):
    self.root = None
  def setRoot(self, node):
    self.root = node
  def getRoot(self):
    return self.root
  def toString(self):
    root = self.getRoot()
    return root.toString()
  def getValue(self):
    return self.getRoot().getValue()
class Node:
  def __init__(self, children):
    self.children = children
  def addChildAtRight(self, child):
    self.children.append(child)
  def getOrderedChildren(self):
    return self.children[ : ]
  def getIthChild(self, i):
    return self.children[i]
  def getName(self):
    return "N/A"
  def getStringComponents(self):
    children = self.getOrderedChildren()
    child_str_list = [x.toString() for x in children]
    components_list = [self.getName()] + child_str_list
    return components_list
  def toString(self):
    components_list = self.getStringComponents()
    if len(components_list) == 1:
      return components_list[0]
    joined_str = string.join(components_list, " ")
    overall_str = "(" + joined_str + ")"
    return overall_str
  def getValue(self):
    pass
  def error(self):
    raise Exception()
  def isURIReferenceNode(self):
    return False
  def isHierPartNode(self):
    return False
  def isURINode(self):
    return False
  def isURIHelper1Node(self):
    return False
  def isURIHelper2Node(self):
    return False
  def isRelativeRefNode(self):
    return False
  def isAuthorityNode(self):
    return False
  def isAuthorityHelper1Node(self):
    return False
  def isAuthorityHelper2Node(self):
    return False
  def isPathAbEmptyNode(self):
    return False
  def isPathAbEmptyHelperNode(self):
    return False
  def isPathAbsoluteNode(self):
    return False
  def isPathAbsoluteHelper1Node(self):
    return False
  def isPathAbsoluteHelper2Node(self):
    return False
  def isPathAbsoluteHelper2bNode(self):
    return False
  def isPathNoSchemeNode(self):
    return False
  def isPathNoSchemeHelper1Node(self):
    return False
  def isPathNoSchemeHelper1bNode(self):
    return False
  def isPathRootlessNode(self):
    return False
  def isPathRootlessHelper1Node(self):
    return False
  def isPathRootlessHelper1bNode(self):
    return False
def normalizePathDict(path_dict):
  segments = path_dict["segments"]
  next_segments = list(segments)
  path_dict["segments"] = next_segments
  return path_dict
class URIReferenceNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "uri_reference"
  def getValue(self):
    children = self.getOrderedChildren()
    child = children[0]
    return child.getValue()
  def isURIReferenceNode(self):
    return True
class HierPartNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "hier_part"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 2:
      authority_node = children[0]
      path_abempty_node = children[1]
      value = {"authority": authority_node.getValue(), "path": normalizePathDict(path_abempty_node.getValue())}
      return value
    elif len(children) == 1:
      child1 = children[0]
      if child1.isPathAbsoluteNode() == True:
        path_absolute_node = child1
        value = {"path": normalizePathDict(path_absolute_node.getValue())}
        return value
      elif child1.isPathRootlessNode() == True:
        path_rootless_node = child1
        value = {"path": normalizePathDict(path_rootless_node.getValue())}
        return value
      else:
        self.error()
    elif len(children) == 0:
      value = {"path": normalizePathDict({"type": "absolute", "segments": deque(), "ends_in_ts": False})}
      return value
    else:
      self.error()
  def isHierPartNode(self):
    return True
class URINode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "uri"
  def getValue(self):
    children = self.getOrderedChildren()
    scheme_node = children[0]
    hier_part_node = children[1]
    uri_helper1_node = children[2]
    a = {"scheme": scheme_node.getValue()}
    a.update(hier_part_node.getValue())
    a.update(uri_helper1_node.getValue())
    value = a
    return value
  def isURINode(self):
    return True
class URIHelper1Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "uri_helper1"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 1:
      uri_helper2_node = children[0]
      value = uri_helper2_node.getValue()
      return value
    elif len(children) == 2:
      query_node = children[0]
      uri_helper2_node = children[1]
      a = {"query": query_node.getValue()}
      a.update(uri_helper2_node.getValue())
      value = a
      return value
    else:
      self.error()
  def isURIHelper1Node(self):
    return True
class URIHelper2Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "uri_helper2"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {}
      return value
    elif len(children) == 1:
      frag_node = children[0]
      value = {"frag": frag_node.getValue()}
      return value
    else:
      self.error()
  def isURIHelper2Node(self):
    return True
class RelativeRefNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "relative_ref"
  def getValue(self):
    children = self.getOrderedChildren()
    relative_part_node = children[0]
    uri_helper1_node = children[1]
    a = relative_part_node.getValue()
    a.update(uri_helper1_node.getValue())
    value = a
    return value
  def isRelativeRefNode(self):
    return True
class RelativePartNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "relative_part"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 2:
      authority_node = children[0]
      path_abempty_node = children[1]
      value = {"authority": authority_node.getValue(), "path": normalizePathDict(path_abempty_node.getValue())}
      return value
    elif len(children) == 1:
      child1 = children[0]
      if child1.isPathAbsoluteNode() == True:
        path_absolute_node = child1
        value = {"path": normalizePathDict(path_absolute_node.getValue())}
        return value
      elif child1.isPathNoSchemeNode() == True:
        path_noscheme_node = child1
        value = {"path": normalizePathDict(path_noscheme_node.getValue())}
        return value
      else:
        self.error()
    elif len(children) == 0:
      value = {"path": normalizePathDict({"type": "relative", "segments": deque(), "ends_in_ts": False})}
      return value
    else:
      self.error()
  def isRelativePartNode(self):
    return True
class AuthorityNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "authority"
  def getValue(self):
    children = self.getOrderedChildren()
    authority_helper1_node = children[0]
    authority_helper2_node = children[1]
    a = authority_helper1_node.getValue()
    a.update(authority_helper2_node.getValue())
    value = a
    return value
  def isAuthorityNode(self):
    return True
class AuthorityHelper1Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "authority_helper1"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {}
      return value
    elif len(children) == 1:
      userinfo_node = children[0]
      value = {"userinfo": userinfo_node.getValue()}
      return value
    else:
      self.error()
  def isAuthorityHelper1Node(self):
    return True
class AuthorityHelper2Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "authority_helper2"
  def getValue(self):
    children = self.getOrderedChildren()
    child = children[0]
    if child.isHostWithPortNode() == True:
      host_with_port_node = child
      value = {"host_with_port": host_with_port_node.getValue()}
      return value
    elif child.isHostWithoutPortNode() == True:
      host_without_port_node = child
      value = {"host_without_port": host_without_port_node.getValue()}
      return value
    else:
      self.error()
  def isAuthorityHelper2Node(self):
    return True
class PathAbEmptyNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_abempty"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {"type": "absolute", "segments": deque(), "ends_in_ts": False}
      return value
    elif len(children) == 1:
      path_abempty_helper_node = children[0]
      a = path_abempty_helper_node.getValue()
      # had a mistake here
      a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]
      value = a
      return value
    else:
      self.error()
  def isPathAbEmptyNode(self):
    return True
class PathAbEmptyHelperNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_abempty_helper"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 2:
      segment_node = children[0]
      path_abempty_node = children[1]
      a = path_abempty_node.getValue()
      a["segments"].appendleft(segment_node.getValue())
      a["type"] = "absolute"
      value = a
      return value
    elif len(children) == 1:
      path_abempty_node = children[0]
      value = path_abempty_node.getValue()
      return value
    else:
      self.error()
  def isPathAbEmptyHelperNode(self):
    return True
class PathAbsoluteNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_absolute"
  def getValue(self):
    children = self.getOrderedChildren()
    path_absolute_helper1_node = children[0]
    a = path_absolute_helper1_node.getValue()
    a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]
    value = a
    return value
  def isPathAbsoluteNode(self):
    return True
class PathAbsoluteHelper1Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_absolute_helper1"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {"type": "absolute", "segments": deque(), "ends_in_ts": False}
      return value
    elif len(children) == 2:
      segment_nz_node = children[0]
      path_absolute_helper2_node = children[1]
      a = path_absolute_helper2_node.getValue()
      a["segments"].appendleft(segment_nz_node.getValue())
      value = a
      return value
    else:
      self.error()
  def isPathAbsoluteHelper1Node(self):
    return True
class PathAbsoluteHelper2Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_absolute_helper2"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {"type": "absolute", "segments": deque(), "ends_in_ts": False}
      return value
    elif len(children) == 1:
      path_absolute_helper2b_node = children[0]
      a = path_absolute_helper2b_node.getValue()
      a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]
      value = a
      return value
    else:
      self.error()
  def isPathAbsoluteHelper2Node(self):
    return True
class PathAbsoluteHelper2bNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_absolute_helper2b"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 2:
      segment_node = children[0]
      path_absolute_helper2_node = children[1]
      a = path_absolute_helper2_node.getValue()
      a["segments"].appendleft(segment_node.getValue())
      value = a
      return a
    elif len(children) == 1:
      path_absolute_helper2_node = children[0]
      value = path_absolute_helper2_node.getValue()
      return value
    else:
      self.error()
  def isPathAbsoluteHelper2bNode(self):
    return True
class PathNoSchemeNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_noscheme"
  def getValue(self):
    children = self.getOrderedChildren()
    segment_nz_nc_node = children[0]
    path_noscheme_helper1_node = children[1]
    a = path_noscheme_helper1_node.getValue()
    a["segments"].appendleft(segment_nz_nc_node.getValue())
    value = a
    return value
  def isPathNoSchemeNode(self):
    return True
class PathNoSchemeHelper1Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_noscheme_helper1"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {"type": "relative", "segments": deque(), "ends_in_ts": False}
      return value
    elif len(children) == 1:
      path_noscheme_helper_1b_node = children[0]
      a = path_noscheme_helper_1b_node.getValue()
      a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]
      value = a
      return value
    else:
      self.error()
  def isPathNoSchemeHelper1Node(self):
    return True
class PathNoSchemeHelper1bNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_noscheme_helper1b"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 1:
      path_noscheme_helper1_node = children[0]
      value = path_noscheme_helper1_node.getValue()
      return value
    elif len(children) == 2:
      segment_node = children[0]
      path_noscheme_helper1_node = children[1]
      a = path_noscheme_helper1_node.getValue()
      a["segments"].appendleft(segment_node.getValue())
      value = a
      return value
    else:
      self.error()
  def isPathNoSchemeHelper1bNode(self):
    return True
class PathRootlessNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_rootless"
  def getValue(self):
    children = self.getOrderedChildren()
    segment_nz_node = children[0]
    path_rootless_helper1_node = children[1]
    a = path_rootless_helper1_node.getValue()
    a["segments"].appendleft(segment_nz_node.getValue())
    value = a
    return value
  def isPathRootlessNode(self):
    return True
class PathRootlessHelper1Node(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_rootless_helper1"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 0:
      value = {"type": "relative", "segments": deque(), "ends_in_ts": False}
      return value
    elif len(children) == 1:
      path_rootless_helper1b = children[0]
      a = path_rootless_helper1b.getValue()
      a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]
      value = a
      return value
    else:
      self.error()
  def isPathRootlessHelper1Node(self):
    return True
class PathRootlessHelper1bNode(Node):
  def __init__(self):
    Node.__init__(self, [])
  def getName(self):
    return "path_rootless_helper1b"
  def getValue(self):
    children = self.getOrderedChildren()
    if len(children) == 1:
      path_rootless_helper1_node = children[0]
      value = path_rootless_helper1_node.getValue()
      return value
    elif len(children) == 2:
      segment_node = children[0]
      path_rootless_helper1_node = children[1]
      a = path_rootless_helper1_node.getValue()
      a["segments"].appendleft(segment_node.getValue())
      value = a
      return value
    else:
      self.error()
  def isPathRootlessHelper1bNode(self):
    return True
"""
RULES ASSOCIATED WITH EPSILON
non-terminals with epsilon in their FIRST set
uri_reference -> relative_ref
hier_part -> EPSILON
uri_helper1 -> uri_helper2
uri_helper2 -> EPSILON
relative_part -> EPSILON
authority_helper1 -> EPSILON
path_abempty -> EPSILON
path_abempty_helper -> path_abempty
path_absolute_helper1 -> EPSILON
path_absolute_helper2 -> EPSILON
path_absolute_helper2b -> path_absolute_helper2
path_noscheme_helper1 -> EPSILON
path_noscheme_helper1b -> path_noscheme_helper1
path_rootless_helper1 -> EPSILON
path_rootless_helper1b -> path_rootless_helper1
authority -> authority_helper1 authority_helper2
relative_ref -> relative_part uri_helper1
special handling
uri_reference -> relative_ref
uri_helper1 -> uri_helper2
path_abempty_helper -> path_abempty
path_absolute_helper2b -> path_absolute_helper2
path_noscheme_helper1b -> path_noscheme_helper1
path_rootless_helper1b -> path_rootless_helper1
authority -> authority_helper1 authority_helper2
relative_ref -> relative_part uri_helper1
"""
"""
PARSER OUTPUT FORMAT
{["scheme": SCHEME], ["authority": {["userinfo": USERINFO], ["host_with_port": HOST_WITH_PORT] | ["host_without_port": HOST_WITHOUT_PORT]}, ["path": {"type": TYPE, "segments": SEGMENTS, "ends_in_ts": ENDS_IN_TS}], ["query": QUERY], ["frag": FRAG]}
GRAMMAR WITH SEMANTIC ACTIONS
uri_reference -> uri { uri_reference.value = uri.value }
	| relative_ref { uri_reference.value = relative_ref.value }
	;
hier_part -> '//' authority path_abempty { hier_part.value = {"authority": authority.value, "path": normalizePathDict(path_abempty.value)}; }
	| path_absolute { hier_part.value = {"path": normalizePathDict((path_absolute.value)} }
	| path_rootless { hier_part.value = {"path": normalizePathDict(path_rootless.value)} }
	| EPSILON { hier_part.value = {"path": normalizePathDict({"type": "absolute", "segments": deque(), "ends_in_ts": False})} }
	;
uri -> SCHEME ':' hier_part uri_helper1 ; { a = {"scheme": SCHEME.value}; a.update(hier_part.value).update(uri_helper1.value); uri.value = a }
uri_helper1 -> uri_helper2 { uri_helper1.value = uri_helper2.value }
	| '?' QUERY uri_helper2 { a = {"query": QUERY.value}; a.update(uri_helper2.value); uri_helper1.value = a }
	;
uri_helper2 -> EPSILON { uri_helper2.value = {} }
	| '#' FRAG { uri_helper2.value = {"frag": FRAG.value} }
	;
relative_ref -> relative_part uri_helper1 ; { a = relative_part.value; a.update(uri_helper1.value); relative_ref.value = a }
relative_part -> '//' authority path_abempty { relative_part.value = {"authority": authority.value, "path": normalizePathDict(path_abempty.value)} }
	| path_absolute { relative_part.value = {"path": normalizePathDict(path_absolute.value)} }
	| path_noscheme { relative_part.value = {"path": normalizePathDict(path_noscheme.value)} }
	| EPSILON { relative_part.value = {"path": normalizePathDict({"type": "relative", "segments": deque(), "ends_in_ts": False})} }
	;
authority -> authority_helper1 authority_helper2 ; { a = authority_helper1.value; a.update(authority_helper2.value); authority.value = a }
authority_helper1 -> EPSILON { authority_helper1.value = {} }	
	| USERINFO '@' { authority_helper1.value = {"userinfo": USERINFO.value } }
	;
	authority_helper2 -> HOST_WITH_PORT { authority_helper2.value = {"host_with_port": HOST_WITH_PORT.value} }
	| HOST_WITHOUT_PORT { authority_helper2.value = {"host_without_port": HOST_WITHOUT_PORT.value} }
	;
path_abempty -> EPSILON { path_abempty.value = {"type": "absolute", "segments": deque(), "ends_in_ts": False} }
	| '/' path_abempty_helper { a = path_abempty_helper.value; a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]; path_abempty.value = a }
	;
path_abempty_helper -> SEGMENT path_abempty { a = path_abempty.value; a["segments"].appendleft(SEGMENT.value); a["type"] = "absolute"; path_abempty_helper.value = a }
	| path_abempty { path_abempty_helper.value = path_abempty.value }
	;
path_absolute -> '/' path_absolute_helper1 ; { a = path_absolute_helper1.value; a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]; path_absolute.value = a }
path_absolute_helper1 -> EPSILON { path_absolute_helper1.value = {"type": "absolute", "segments": deque(), "ends_in_ts": False} }
	| SEGMENT_NZ path_absolute_helper2 { a = path_absolute_helper2.value; a["segments"].appendleft(SEGMENT_NZ.value); path_absolute_helper1.value = a }
	;
path_absolute_helper2 -> EPSILON { path_absolute_helper2.value = {"type": "absolute", "segments": deque(), "ends_in_ts": False} }
	| '/' path_absolute_helper2b { a = path_absolute_helper2b.value; a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]; path_absolute_helper2.value = a }
	;
path_absolute_helper2b -> SEGMENT path_absolute_helper2 { a = path_absolute_helper2.value; a["segments"].appendleft(SEGMENT.value); path_absolute_helper2b.value = a }
	| path_absolute_helper2 { path_absolute_helper2b.value = path_absolute_helper2.value }
	;
path_noscheme -> SEGMENT_NZ_NC path_noscheme_helper1 ; { a = path_noscheme_helper1.value; a["segments"].appendleft(SEGMENT_NZ_NC.value); path_noscheme.value = a }
path_noscheme_helper1 -> EPSILON { path_noscheme_helper1.value = {"type": "relative", "segments": deque(), "ends_in_ts": False} }
	| '/' path_noscheme_helper1b { a = path_noscheme_helper1b.value; a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]; path_noscheme_helper1.value = a }
	;
path_noscheme_helper1b -> path_noscheme_helper1 { path_noscheme_helper1b.value = path_noscheme_helper1.value }
	| SEGMENT path_noscheme_helper1 { a = path_noscheme_helper1.value; a["segments"].appendleft(SEGMENT.value); path_noscheme_helper1b.value = a }
	;
path_rootless -> SEGMENT_NZ path_rootless_helper1 ; { a = path_rootless_helper1.value; a["segments"].appendleft(SEGMENT_NZ.value); path_rootless.value = a }
path_rootless_helper1 -> EPSILON { path_rootless_helper1.value = {"type": "relative", "segments": deque(), "ends_in_ts": False} }
	| '/' path_rootless_helper1b { a = path_rootless_helper1b.value; a["ends_in_ts"] = True if len(a["segments"]) == 0 else a["ends_in_ts"]; path_rootless_helper1.value = a }
	;
path_rootless_helper1b -> path_rootless_helper1 { path_rootless_helper1b.value = path_rootless_helper1.value }
	| SEGMENT path_rootless_helper1 { a = path_rootless_helper1.value; a["segments"].appendleft(SEGMENT.value); path_rootless_helper1b.value = a }
	;
"""
class Parser:
  def __init__(self, tokens, FIRST, FOLLOW):
    self.token_deque = deque(tokens)
    self.first = FIRST
    self.follow = FOLLOW
  def getFirstSets(self):
    return self.first
  def getFollowSets(self):
    return self.follow
  def parse(self):
    root_node = self.URIReference()
    tree = ParseTree()
    tree.setRoot(root_node)
    return tree
  def SEGMENT_NZ_NC(self):
    token = self._getNextToken()
    node = token
    if node.isSegmentNZNCNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def SCHEME(self):
    token = self._getNextToken()
    node = token
    if node.isSchemeNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def USERINFO(self):
    token = self._getNextToken()
    node = token
    if node.isUserInfoNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def HOST_WITH_PORT(self):
    token = self._getNextToken()
    node = token
    if node.isHostWithPortNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def HOST_WITHOUT_PORT(self):
    token = self._getNextToken()
    node = token
    if node.isHostWithoutPortNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def SEGMENT_NZ(self):
    token = self._getNextToken()
    node = token
    if node.isSegmentNZNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def SEGMENT(self):
    token = self._getNextToken()
    node = token
    if node.isSegmentNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def QUERY(self):
    token = self._getNextToken()
    node = token
    if node.isQueryNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def FRAG(self):
    token = self._getNextToken()
    node = token
    if node.isFragNode() == True:
      self._removeNextToken()
    else:
      self.error()
    return node
  def URIReference(self):
    curr_token = self._getLookaheadToken()
    node = URIReferenceNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol in FIRST["uri"]:
      uri_node = self.URI()
      node.addChildAtRight(uri_node)
    elif symbol in FIRST["relative_ref"] or symbol in FOLLOW["uri_reference"]:
      relative_ref_node = self.relativeRef()
      node.addChildAtRight(relative_ref_node)
    else:
      self.error()
    return node
  def hierPart(self):
    curr_token = self._getLookaheadToken()
    node = HierPartNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == "//":
      self.scan("//")
      authority_node = self.authority()
      path_abempty_node = self.pathAbEmpty()
      node.addChildAtRight(authority_node)
      node.addChildAtRight(path_abempty_node)
    elif symbol in FIRST["path_absolute"]:
      path_absolute_node = self.pathAbsolute()
      node.addChildAtRight(path_absolute_node)
    elif symbol in FIRST["path_rootless"]:
      path_rootless_node = self.pathRootless()
      node.addChildAtRight(path_rootless_node)
    elif symbol in FOLLOW["hier_part"]:
      pass
    else:
      self.error()
    return node
  def URI(self):
    curr_token = self._getLookaheadToken()
    node = URINode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    scheme_node = self.SCHEME()
    self.scan(':')
    hier_part_node = self.hierPart()
    uri_helper1_node = self.URIHelper1()
    node.addChildAtRight(scheme_node)
    node.addChildAtRight(hier_part_node)
    node.addChildAtRight(uri_helper1_node)
    return node
  def URIHelper1(self):
    curr_token = self._getLookaheadToken()
    node = URIHelper1Node()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol in FIRST["uri_helper2"] or symbol in FOLLOW["uri_helper1"]:
      uri_helper2_node = self.URIHelper2()
      node.addChildAtRight(uri_helper2_node)
    elif symbol == '?':
      self.scan('?')
      query_node = self.QUERY()
      uri_helper2_node = self.URIHelper2()
      node.addChildAtRight(query_node)
      node.addChildAtRight(uri_helper2_node)
    else:
      self.error()
    return node
  def URIHelper2(self):
    curr_token = self._getLookaheadToken()
    node = URIHelper2Node()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol in FOLLOW["uri_helper2"]:
      return node
    elif symbol == '#':
      self.scan('#')
      frag_node = self.FRAG()
      node.addChildAtRight(frag_node)
    else:
      self.error()
    return node
  def relativeRef(self):
    curr_token = self._getLookaheadToken()
    node = RelativeRefNode()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    relative_part_node = self.relativePart()
    uri_helper1_node = self.URIHelper1()
    node.addChildAtRight(relative_part_node)
    node.addChildAtRight(uri_helper1_node)
    return node
  def relativePart(self):
    curr_token = self._getLookaheadToken()
    node = RelativePartNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == "//":
      self.scan("//")
      authority_node = self.authority()
      path_abempty_node = self.pathAbEmpty()
      node.addChildAtRight(authority_node)
      node.addChildAtRight(path_abempty_node)
    elif symbol in FIRST["path_absolute"]:
      path_absolute_node = self.pathAbsolute()
      node.addChildAtRight(path_absolute_node)
    elif symbol in FIRST["path_noscheme"]:
      path_noscheme_node = self.pathNoScheme()
      node.addChildAtRight(path_noscheme_node)
    elif symbol in FOLLOW["relative_part"]:
      pass
    else:
      self.error()
    return node
  def authority(self):
    curr_token = self._getLookaheadToken()
    node = AuthorityNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    authority_helper1_node = self.authorityHelper1()
    authority_helper2_node = self.authorityHelper2()
    node.addChildAtRight(authority_helper1_node)
    node.addChildAtRight(authority_helper2_node)
    return node
  def authorityHelper1(self):
    curr_token = self._getLookaheadToken()
    node = AuthorityHelper1Node()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol in FOLLOW["authority_helper1"]:
      pass
    elif symbol == USERINFO:
      user_info_node = self.USERINFO()
      self.scan('@')
      node.addChildAtRight(user_info_node)
    else:
      self.error()
    return node
  def authorityHelper2(self):
    curr_token = self._getLookaheadToken()
    node = AuthorityHelper2Node()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == HOST_WITH_PORT:
      host_with_port_node = self.HOST_WITH_PORT()
      node.addChildAtRight(host_with_port_node)
    elif symbol == HOST_WITHOUT_PORT:
      host_without_port_node = self.HOST_WITHOUT_PORT()
      node.addChildAtRight(host_without_port_node)
    else:
      self.error()
    return node
  def pathAbEmpty(self):
    curr_token = self._getLookaheadToken()
    node = PathAbEmptyNode()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == '/':
      self.scan('/')
      path_abempty_helper_node = self.pathAbEmptyHelper()
      node.addChildAtRight(path_abempty_helper_node)
    elif symbol in FOLLOW["path_abempty"]:
      pass
    else:
      self.error()
    return node
  def pathAbEmptyHelper(self):
    curr_token = self._getLookaheadToken()
    node = PathAbEmptyHelperNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == SEGMENT:
      segment_node = self.SEGMENT()
      path_abempty_node = self.pathAbEmpty()
      node.addChildAtRight(segment_node)
      node.addChildAtRight(path_abempty_node)
    elif symbol in FIRST["path_abempty"] or symbol in FOLLOW["path_abempty_helper"]:
      path_abempty_node = self.pathAbEmpty()
      node.addChildAtRight(path_abempty_node)
    else:
      self.error()
    return node
  def pathAbsolute(self):
    curr_token = self._getLookaheadToken()
    node = PathAbsoluteNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    self.scan('/')
    path_absolute_helper1_node = self.pathAbsoluteHelper1()
    node.addChildAtRight(path_absolute_helper1_node)
    return node
  def pathAbsoluteHelper1(self):
    curr_token = self._getLookaheadToken()
    node = PathAbsoluteHelper1Node()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == SEGMENT_NZ:
      segment_nz_node = self.SEGMENT_NZ()
      path_absolute_helper2_node = self.pathAbsoluteHelper2()
      node.addChildAtRight(segment_nz_node)
      node.addChildAtRight(path_absolute_helper2_node)
    elif symbol in FOLLOW["path_absolute_helper1"]:
      pass
    else:
      self.error()
    return node
  def pathAbsoluteHelper2(self):
    curr_token = self._getLookaheadToken()
    node = PathAbsoluteHelper2Node()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == '/':
      self.scan('/')
      path_absolute_helper2b_node = self.pathAbsoluteHelper2b()
      node.addChildAtRight(path_absolute_helper2b_node)
    elif symbol in FOLLOW["path_absolute_helper2"]:
      pass
    else:
      self.error()
    return node
  def pathAbsoluteHelper2b(self):
    curr_token = self._getLookaheadToken()
    node = PathAbsoluteHelper2bNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == SEGMENT:
      segment_node = self.SEGMENT()
      path_absolute_helper2_node = self.pathAbsoluteHelper2()
      node.addChildAtRight(segment_node)
      node.addChildAtRight(path_absolute_helper2_node)
    elif symbol in FIRST["path_absolute_helper2"] or symbol in FOLLOW["path_absolute_helper2b"]	:
      path_absolute_helper2_node = self.pathAbsoluteHelper2()
      node.addChildAtRight(path_absolute_helper2)
    else:
      self.error()
    return node
  def pathNoScheme(self):
    curr_token = self._getLookaheadToken()
    node = PathNoSchemeNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    segment_nz_nc_node = self.SEGMENT_NZ_NC()
    path_noscheme_helper1_node = self.pathNoSchemeHelper1()
    node.addChildAtRight(segment_nz_nc_node)
    node.addChildAtRight(path_noscheme_helper1_node)
    return node
  def pathNoSchemeHelper1(self):
    curr_token = self._getLookaheadToken()
    node = PathNoSchemeHelper1Node()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == '/':
      self.scan('/')
      path_noscheme_helper1b_node = self.pathNoSchemeHelper1b()
      node.addChildAtRight(path_noscheme_helper1b_node)
    elif symbol in FOLLOW["path_noscheme_helper1"]:
      pass
    else:
      self.error()
    return node
  def pathNoSchemeHelper1b(self):
    curr_token = self._getLookaheadToken()
    node = PathNoSchemeHelper1bNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol in FIRST["path_noscheme_helper1"] or symbol in FOLLOW["path_noscheme_helper1b"]:
      path_noscheme_helper1_node = self.pathNoSchemeHelper1()
      node.addChildAtRight(path_noscheme_helper1_node)
    elif symbol == SEGMENT:
      segment_node = self.SEGMENT()
      path_noscheme_helper1_node = self.pathNoSchemeHelper1()
      node.addChildAtRight(segment_node)
      node.addChildAtRight(path_noscheme_helper1_node)
    else:
      self.error()
    return node
  def pathRootless(self):
    curr_token = self._getLookaheadToken()
    node = PathRootlessNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    segment_nz_node = self.SEGMENT_NZ()
    path_rootless_helper1_node = self.pathRootlessHelper1()
    node.addChildAtRight(segment_nz_node)
    node.addChildAtRight(path_rootless_helper1_node)
    return node
  def pathRootlessHelper1(self):
    curr_token = self._getLookaheadToken()
    node = PathRootlessHelper1Node()
    FIRST = self.getFirstSets()
    FOLLOW = self.getFollowSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol == '/':
      self.scan('/')
      path_rootless_helper1b_node = self.pathRootlessHelper1b()
      node.addChildAtRight(path_rootless_helper1b_node)
    elif symbol in FOLLOW["path_rootless_helper1"]:
      pass
    else:
      self.error()
    return node
  def pathRootlessHelper1b(self):
    curr_token = self._getLookaheadToken()
    node = PathRootlessHelper1bNode()
    FIRST = self.getFirstSets()
    symbol = Parser.getFIRSTFOLLOWSymbol(curr_token)
    if symbol in FIRST["path_rootless_helper1"] or symbol in FOLLOW["path_rootless_helper1b"]:
      path_rootless_helper1_node = self.pathRootlessHelper1()
      node.addChildAtRight(path_rootless_helper1_node)
    if symbol == SEGMENT:
      segment_node = self.SEGMENT()
      path_rootless_helper1_node = self.pathRootlessHelper1()
      node.addChildAtRight(segment_node)
      node.addChildAtRight(path_rootless_helper1_node)
    else:
      self.error()
    return node
  def error(self):
    raise Exception()
  def scan(self, chars):
    # curr_str = char
    self.matchString(chars)
  def _getTokens(self):
    return self.token_deque
  # if no next token exists, return None
  def _getNextToken(self):
    if len(self.token_deque) == 0:
      return None
    else:
      return self.token_deque[0]
  def _removeNextToken(self):
    self.token_deque.popleft()
  def matchString(self, curr_str):
    next_token = self._getNextToken()
    lexeme = next_token.getLexeme()
    if curr_str == lexeme:
      self._removeNextToken()
    else:
      self.error()
  # if no next token exists, return None
  def _getLookaheadToken(self):
    next_token = self._getNextToken()
    return next_token
  # token may be None, which we interpret as EOF
  @staticmethod
  def getFIRSTFOLLOWSymbol(token):
    if token == None:
      return EOF
    else:
      return token.getFIRSTFOLLOWSymbol()
    # return token.getFIRSTFOLLOWSymbol()
def parse(line, OVERALL_RE, FIRST, FOLLOW):
  tokens = getTokens(line, OVERALL_RE)
  # print tokens
  # print [x.getLexeme() for x in tokens]
  parser = Parser(tokens, FIRST, FOLLOW)
  parse_tree = parser.parse()
  # print parse_tree.toString()
  return parse_tree.getValue()
# TOKEN NODE CLASSES
class TokenNode(Node):
  def __init__(self, lexeme):
    Node.__init__(self, [])
    self.lexeme = lexeme
  def getValue(self):
    return self.getLexeme()
  def getLexeme(self):
    return self.lexeme
  def getFIRSTFOLLOWSymbol(self):
    pass
  def isSegmentNZNCNode(self):
    return False
  def isSchemeNode(self):
    return False
  def isUserInfoNode(self):
    return False
  def isHostWithPortNode(self):
    return False
  def isHostWithoutPortNode(self):
    return False
  def isSegmentNZNode(self):
    return False
  def isSegmentNode(self):
    return False
  def isQueryNode(self):
    return False
  def isFragNode(self):
    return False
  def isMiscNode(self):
    return False
class SegmentNZNCNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return SEGMENT_NZ_NC
  def isSegmentNZNCNode(self):
    return True
class SchemeNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return SCHEME
  def isSchemeNode(self):
    return True
class UserInfoNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return USERINFO
  def isUserInfoNode(self):
    return True
class HostWithPortNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return HOST_WITH_PORT
  def isHostWithPortNode(self):
    return True
class HostWithoutPortNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return HOST_WITHOUT_PORT
  def isHostWithoutPortNode(self):
    return True
class SegmentNZNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return SEGMENT_NZ
  def isSegmentNZNode(self):
    return True
class SegmentNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return SEGMENT
  def isSegmentNode(self):
    return True
class QueryNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return QUERY
  def isQueryNode(self):
    return True
class FragNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return FRAG
  def isFragNode(self):
    return True
class MiscNode(TokenNode):
  def __init__(self, lexeme):
    TokenNode.__init__(self, lexeme)
  def getFIRSTFOLLOWSymbol(self):
    return self.getLexeme()
  def isMiscNode(self):
    return True
def getTokens(lexeme_seq_line, OVERALL_RE):
  curr_line = lexeme_seq_line
  regex = re.compile(OVERALL_RE)
  tokens = []
  curr_pos = 0
  num_chars = len(curr_line)
  while curr_pos != num_chars:
    m = regex.match(curr_line, curr_pos)
    lexeme_text = m.group(0)
    token = None
    if m.group("segment_nz_nc") != None:
      token = SegmentNZNCNode(lexeme_text)
    elif m.group("scheme") != None:
      token = SchemeNode(lexeme_text)
    elif m.group("userinfo") != None:
      token = UserInfoNode(lexeme_text)
    elif m.group("host_with_port") != None:
      token = HostWithPortNode(lexeme_text)
    elif m.group("host_without_port") != None:
      token = HostWithoutPortNode(lexeme_text)
    elif m.group("segment_nz") != None:
      token = SegmentNZNode(lexeme_text)
    elif m.group("segment") != None:
      token = SegmentNode(lexeme_text)
    elif m.group("query") != None:
      token = QueryNode(lexeme_text)
    elif m.group("frag") != None:
      token = FragNode(lexeme_text)
    elif m.group("misc") != None:
      token = MiscNode(lexeme_text)
    if token != None:
      tokens.append(token)
    # curr_line = regex.sub("", curr_line, count = 1)
    token_char_size = len(lexeme_text)
    curr_pos += token_char_size
  return tokens
"""
FIRST
FIRST(uri_reference) = {EPSILON, '//', '/', '?', '#', SCHEME, SEGMENT_NZ_NC}
FIRST(hier_part) = {EPSILON, '//', '/', SEGMENT_NZ}
FIRST(uri) = {SCHEME}
FIRST(uri_helper1) = {EPSILON, '?', '#'}
FIRST(uri_helper2) = {EPSILON, '#'}
FIRST(relative_ref) = {EPSILON, '//', '/', '?', '#', SEGMENT_NZ_NC}
FIRST(relative_part) = {EPSILON, '//', '/', SEGMENT_NZ_NC}
FIRST(authority) = {EPSILON, HOST_WITH_PORT, HOST_WITHOUT_PORT, USERINFO}
FIRST(authority_helper1) = {EPSILON, USERINFO}
FIRST(authority_helper2) = {HOST_WITH_PORT, HOST_WITHOUT_PORT}
FIRST(path_abempty) = {EPSILON, '/'}
FIRST(path_abempty_helper) = {EPSILON, '/', SEGMENT}
FIRST(path_absolute) = {'/'}
FIRST(path_absolute_helper1) = {EPSILON, SEGMENT_NZ}
FIRST(path_absolute_helper2) = {EPSILON, '/'}
FIRST(path_absolute_helper2b) = {EPSILON, '/', SEGMENT_NZ}
FIRST(path_noscheme) = {SEGMENT_NZ_NC}
FIRST(path_noscheme_helper1) = {EPSILON, '/'}
FIRST(path_noscheme_helper1b) = {EPSILON, '/', SEGMENT}
FIRST(path_rootless) = {SEGMENT_NZ}
FIRST(path_rootless_helper1) = {EPSILON, '/'}
FIRST(path_rootless_helper1b) = {EPSILON, '/', SEGMENT}
FOLLOW
FOLLOW(uri_reference) = {EOF}
FOLLOW(hier_part) = {'?', '#', EOF}
FOLLOW(uri) = {EOF}
FOLLOW(uri_helper1) = {EOF}
FOLLOW(uri_helper2) = {EOF}
FOLLOW(relative_ref) = {EOF}
FOLLOW(relative_part) = {'?', '#', EOF}
FOLLOW(authority) = {'/', '?', '#', EOF}
FOLLOW(authority_helper1) = {HOST_WITH_PORT, HOST_WITHOUT_PORT}
FOLLOW(authority_helper2) = {'/', '?', '#', EOF}
FOLLOW(path_abempty) = {'?', '#', EOF}
FOLLOW(path_abempty_helper) = {'?', '#', EOF}
FOLLOW(path_absolute) = {'?', '#', EOF}
FOLLOW(path_absolute_helper1) = {'?', '#', EOF}
FOLLOW(path_absolute_helper2) = {'?', '#', EOF}
FOLLOW(path_absolute_helper2b) = {'?', '#', EOF}
FOLLOW(path_noscheme) = {'?', '#', EOF}
FOLLOW(path_noscheme_helper1) = {'?', '#', EOF}
FOLLOW(path_noscheme_helper1b) = {'?', '#', EOF}
FOLLOW(path_rootless) = {'?', '#', EOF}
FOLLOW(path_rootless_helper1) = {'?', '#', EOF}
FOLLOW(path_rootless_helper1b) = {'?', '#', EOF}
"""
FIRST = {}
FOLLOW = {}
FIRST["uri_reference"] = {EPSILON, '//', '/', '?', '#', SCHEME, SEGMENT_NZ_NC}
FIRST["hier_part"] = {EPSILON, '//', '/', SEGMENT_NZ}
FIRST["uri"] = {SCHEME}
FIRST["uri_helper1"] = {EPSILON, '?', '#'}
FIRST["uri_helper2"] = {EPSILON, '#'}
FIRST["relative_ref"] = {EPSILON, '//', '/', '?', '#', SEGMENT_NZ_NC}
FIRST["relative_part"] = {EPSILON, '//', '/', SEGMENT_NZ_NC}
FIRST["authority"] = {EPSILON, HOST_WITH_PORT, HOST_WITHOUT_PORT, USERINFO}
FIRST["authority_helper1"] = {EPSILON, USERINFO}
FIRST["authority_helper2"] = {HOST_WITH_PORT, HOST_WITHOUT_PORT}
FIRST["path_abempty"] = {EPSILON, '/'}
FIRST["path_abempty_helper"] = {EPSILON, '/', SEGMENT}
FIRST["path_absolute"] = {'/'}
FIRST["path_absolute_helper1"] = {EPSILON, SEGMENT_NZ}
FIRST["path_absolute_helper2"] = {EPSILON, '/'}
FIRST["path_absolute_helper2b"] = {EPSILON, '/', SEGMENT_NZ}
FIRST["path_noscheme"] = {SEGMENT_NZ_NC}
FIRST["path_noscheme_helper1"] = {EPSILON, '/'}
FIRST["path_noscheme_helper1b"] = {EPSILON, '/', SEGMENT}
FIRST["path_rootless"] = {SEGMENT_NZ}
FIRST["path_rootless_helper1"] = {EPSILON, '/'}
FIRST["path_rootless_helper1b"] = {EPSILON, '/', SEGMENT}
# FIRST["path_empty"] = {EPSILON}
FOLLOW["uri_reference"] = {EOF}
FOLLOW["hier_part"] = {'?', '#', EOF}
FOLLOW["uri"] = {EOF}
FOLLOW["uri_helper1"] = {EOF}
FOLLOW["uri_helper2"] = {EOF}
FOLLOW["relative_ref"] = {EOF}
FOLLOW["relative_part"] = {'?', '#', EOF}
FOLLOW["authority"] = {'/', '?', '#', EOF}
FOLLOW["authority_helper1"] = {HOST_WITH_PORT, HOST_WITHOUT_PORT}
FOLLOW["authority_helper2"] = {'/', '?', '#', EOF}
FOLLOW["path_abempty"] = {'?', '#', EOF}
FOLLOW["path_abempty_helper"] = {'?', '#', EOF}
FOLLOW["path_absolute"] = {'?', '#', EOF}
FOLLOW["path_absolute_helper1"] = {'?', '#', EOF}
FOLLOW["path_absolute_helper2"] = {'?', '#', EOF}
FOLLOW["path_absolute_helper2b"] = {'?', '#', EOF}
FOLLOW["path_noscheme"] = {'?', '#', EOF}
FOLLOW["path_noscheme_helper1"] = {'?', '#', EOF}
FOLLOW["path_noscheme_helper1b"] = {'?', '#', EOF}
FOLLOW["path_rootless"] = {'?', '#', EOF}
FOLLOW["path_rootless_helper1"] = {'?', '#', EOF}
FOLLOW["path_rootless_helper1b"] = {'?', '#', EOF}
# FOLLOW["path_empty"] = {'?', '#', EOF}
def main():
  stream = sys.stdin
  line = stream.readline()
  # line = "http://www.hello.com/hello1/hello2/?hello#hello"
  # line = "ftp://ftp.is.co.za/rfc/rfc1808.txt"
  # line = "http://www.ietf.org/rfc/rfc2396.txt"
  # line = "ldap://[2001:db8::7]/c=GB?objectClass?one"
  # line = "mailto:John.Doe@example.com"
  # line = "news:comp.infosystems.www.servers.unix"
  # line = "tel:+1-816-555-1212"
  # line = "telnet://192.0.2.16:80/"
  # line = "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"
  # line = "a/b/../c"
  # line = "a"
  # line = ""
  # line = "ldap:/a"
  # line = "http://www.google.com/"
  # line = "http://www.%2b.com
  # line = "/a/b/c/./../../g"
  # line = "http://a/b/c/d;p?y"
  # line = "?y"
  # tokens = getTokens(line, OVERALL_RE)
  # print tokens
  value = parse(line, OVERALL_RE, FIRST, FOLLOW)
  print value
if __name__ == "__main__":
  main()
