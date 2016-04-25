# 2016-04-23

# in accordance with rfc 3986, 17.13.4 of html 4.01 specification w3c recommendation

# trailing forward slash is important, via sec. 6.2.3 of rfc 3986

# requires publicsuffix module

# inspired by todd cullen, rohit rajan, w. david jarvis

"""
PARSER OUTPUT FORMAT
{["scheme": SCHEME], ["authority": {["userinfo": USERINFO], ["host_with_port": HOST_WITH_PORT] | ["host_without_port": HOST_WITHOUT_PORT]}, ["path": {"type": TYPE, "segments": SEGMENTS, "ends_in_ts": ENDS_IN_TS}], ["query": QUERY], ["frag": FRAG]}
"""
import uri_parser
import sys
import re
import string
from collections import deque
from collections import defaultdict
from publicsuffix import PublicSuffixList
USERINFO_COMPONENT = 0
HTTP_USER_COMPONENT = 1
HTTP_PASSWORD_COMPONENT = 2
HOST_COMPONENT = 3
SEGMENT_COMPONENT = 4
PATH_NO_SCHEME_FIRST_SEGMENT_COMPONENT = 5
QUERY_COMPONENT = 6
HTTP_QUERY_KEY_COMPONENT = 7
HTTP_QUERY_VALUE_COMPONENT = 8
FRAGMENT_COMPONENT = 9
NOT_A_COMPONENT = 10
# for percent-encoding
# have allowed characters, then over-riding banning of certain characters (current-level external and internal)
USERINFO_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:])(?![/@])"
HTTP_USER_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:])(?![/@:])"
HTTP_PASSWORD_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:])(?![@:])"
HOST_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[\[\]:])(?![@/?#])"
SEGMENT_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:@])(?![/?#])"
PATH_NO_SCHEME_FIRST_SEGMENT_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[@])(?![/?#])"
QUERY_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:@/?])(?![#+])"
HTTP_QUERY_KEY_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:@/?])(?![#&=+])"
HTTP_QUERY_VALUE_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:@/?])(?![#&=+])"
FRAGMENT_SAFE_RE = r"(?=[a-zA-Z0-9\-._~]|[!$&'()*+,;=]|[:@/?])(?![#])"
# note that an empty string passed as pattern to percentEncode() will always lead to matches and so nothing will be percent-encoded
class URI:
  def __init__(self, scheme, authority, path, query, fragment):
    self.scheme = scheme
    self.authority = authority
    self.path = path
    self.query = query
    self.fragment = fragment
  @staticmethod
  def constructUsingStrHelper(uri_str):
    is_valid = URI.checkURIIsValid(uri_str)
    # print uri_str
    parser_output = None
    if is_valid == True:
      parser_output = URI._getParserOutput(uri_str)
      # print parser_output
    else:
      raise Exception()
    return parser_output
  @staticmethod
  def constructUsingStr(uri_str):
    parser_output = URI.constructUsingStrHelper(uri_str)
    uri = URI.constructFromParserOutput(parser_output)
    return uri
  @staticmethod
  def _constructFromParserOutputHelper(parser_output, uri):
    uri._createScheme(parser_output)
    uri._createAuthority(parser_output)
    uri._createPath(parser_output)
    uri._createQuery(parser_output)
    uri._createFragment(parser_output)
  @staticmethod
  def constructFromParserOutput(parser_output):
    uri = URI(None, None, None, None, None)
    URI._constructFromParserOutputHelper(parser_output, uri)
    return uri
  # retrieve a (scheme, authority, path, query, fragment) tuple
  def getComponents(self):
    scheme = self.getScheme()
    authority = self.getAuthority()
    path = self.getPath()
    query = self.getQuery()
    fragment = self.getFragment()
    result = (scheme, authority, path, query, fragment)
    return result
  def _createScheme(self, parser_output):
    self.scheme = Scheme.constructFromParserOutput(parser_output)
  def _createAuthority(self, parser_output):
    self.authority = Authority.constructFromParserOutput(parser_output, False)
  def _createPath(self, parser_output):
    self.path = Path.constructFromParserOutput(parser_output)
  def _createQuery(self, parser_output):
    self.query = Query.constructFromParserOutput(parser_output, False)
  def _createFragment(self, parser_output):
    self.fragment = Fragment.constructFromParserOutput(parser_output)
  @staticmethod
  def _getParserOutput(uri_str):
    overall_re = uri_parser.OVERALL_RE
    first = uri_parser.FIRST
    follow = uri_parser.FOLLOW
    value = uri_parser.parse(uri_str, overall_re, first, follow)
    return value
  def _getSchemeCopy(self):
    if self.haveScheme() == True:
      return self.getScheme().copy()
    else:
      return None
  def _getAuthorityCopy(self, get_for_http_uri):
    if self.haveAuthority() == True:
      authority = None
      if get_for_http_uri == True:
        authority = self.getAuthority().getForHTTPURI()
      else:
        authority = self.getAuthority().copy()
      return authority
    else:
      return None
  def _getPathCopy(self):
    if self.havePath() == True:
      return self.getPath().copy()
    else:
      return None
  def _getQueryCopy(self, get_for_http_uri):
    if self.haveQuery() == True:
      query = None
      if get_for_http_uri == True:
        query = self.getQuery().getForHTTPURI()
      else:
        query = self.getQuery().copy()
      return query
    else:
      return None
  def _getFragmentCopy(self):
    if self.haveFragment() == True:
      return self.getFragment().copy()
    else:
      return None
  def getScheme(self):
    return self.scheme
  # getters and setters; components may be None if undefined
  def getAuthority(self):
    return self.authority
  def getPath(self):
    return self.path
  def getQuery(self):
    return self.query
  def getFragment(self):
    return self.fragment
  def setScheme(self, scheme):
    self.scheme = scheme
  def setAuthority(self, authority):
    self.authority = authority
  def setPath(self, path):
    self.path = path
  def setQuery(self, query):
    self.query = query
  def setFragment(self, fragment):
    self.fragment = fragment
  def haveScheme(self):
    return self.getScheme() != None
  def haveAuthority(self):
    return self.getAuthority() != None
  def havePath(self):
    return self.getPath() != None
  def haveQuery(self):
    return self.getQuery() != None
  def haveFragment(self):
    return self.getFragment() != None
  def _isARelativeReference(self):
    # know if we are a relative reference based on whether or not we have a scheme
    scheme = self.getScheme()
    is_relative = scheme == None
    return is_relative
  # we assume base uri ends in a directory; 
  # ends_in_directory refers to relative reference;
  # only works if current URI is a relative reference
  # if we are non-strict, reference can have a scheme
  def resolve(self, base_uri_with_fragment, is_strict):
    scheme_is_http = base_uri_with_fragment.isHTTPURI()
    # strip a base uri so that it does not have a fragment
    base_uri = base_uri_with_fragment.copy()
    base_uri.setFragment(None)
    T = base_uri.copy()
    R = self
    if is_strict == False and R.haveScheme() == True and R.getScheme().isEquivalentTo(base_uri.getScheme()):
      R.setScheme(None)
    if R.haveScheme() == True:
      T.setScheme(R._getSchemeCopy())
      T.setAuthority(R._getAuthorityCopy(scheme_is_http))
      path = R._getPathCopy()
      end_in_trailing_slash = path.removeDotSegmentsAndUpdateTrailingSlashStatus()
      T.setPath(path)
      T.setQuery(R._getQueryCopy(scheme_is_http))
    else:
      if R.haveAuthority() == True:
        T.setAuthority(R._getAuthorityCopy(scheme_is_http))
        path = R._getPathCopy()
        path.removeDotSegmentsAndUpdateTrailingSlashStatus()
        T.setPath(path)
        T.setQuery(R._getQueryCopy(scheme_is_http))
      else:
        if R.getPath().haveSegments() == False:
          T.setPath(base_uri._getPathCopy())
          if R.haveQuery() == True:
            T.setQuery(R._getQueryCopy(scheme_is_http))
          else:
            T.setQuery(base_uri._getQueryCopy(scheme_is_http))
        else:
          if R.getPath().getPathType() == ABSOLUTE:
            path = R._getPathCopy()
            path.removeDotSegmentsAndUpdateTrailingSlashStatus()
            T.setPath(path)
          else:
            path = URI.merge(base_uri, R)
            path.removeDotSegmentsAndUpdateTrailingSlashStatus()
            T.setPath(path)
          T.setQuery(R._getQueryCopy(scheme_is_http))
        T.setAuthority(base_uri._getAuthorityCopy(scheme_is_http))
      T.setScheme(base_uri._getSchemeCopy())
    T.setFragment(R._getFragmentCopy())
    return T
  # returns a path object
  @staticmethod
  def merge(base_uri, relative_reference):
    # assume that base uri has absolute path
    bu_path = base_uri.getPath()
    result_path = bu_path.copy()
    if result_path.getPathType() != ABSOLUTE:
      raise Exception()
    rr_path = relative_reference.getPath()
    rr_segment_unencoded_str_list = rr_path.getSegmentUnencodedStrList()
    if bu_path.haveSegments() == True:
      result_path.popSegment()
    for segment_unencoded_str in rr_segment_unencoded_str_list:
      result_path.pushSegment(segment_unencoded_str)
    ends_in_trailing_slash = rr_path.getEndsInTrailingSlash()
    result_path.setEndsInTrailingSlash(ends_in_trailing_slash)
    return result_path
  # perform percent encoding
  def toString(self, do_case_normalize = False, do_query_normalizing = False):
    scheme = self.getScheme()
    authority = self.getAuthority()
    path = self.getPath()
    query = self.getQuery()
    fragment = self.getFragment()
    result = ""
    if self.haveScheme() == True:
      result += scheme.toString(do_case_normalize)
      result += ":"
    if self.haveAuthority() == True:
      result += "//"
      result += authority.toString(do_case_normalize)
    result += path.toString(self.haveScheme())
    if self.haveQuery() == True:
      result += "?"
      if do_query_normalizing == True:
        result += self.getNormalizedQueryString()
      else:
        result += self.getNonNormalizedQueryString()
    if self.haveFragment() == True:
      result += "#"
      result += fragment.toString()
    return result
  def getNormalizedQueryString(self):
    return self.getQuery().toString()
  def getNonNormalizedQueryString(self):
    return self.getQuery().toString()
  # perform percent encoding
  # perform syntax-related normalization (dot-segment removal, percent-decoding of encoded unreserved characters, case), semantic normalization (sorting of query parameters by key)
  def toNormalizedString(self):
    uri = self.copy()
    path = uri.getPath()
    path.removeDotSegmentsAndUpdateTrailingSlashStatus()
    result = uri.toString(True, True)
    return result
  # compare with a different uri
  def isEquivalentTo(self, uri):
    uri_str1 = self.toNormalizedString()
    uri_str2 = uri.toNormalizedString()
    does_match = uri_str1 == uri_str2 and self.isOfSameType(uri)
    return does_match
  # check that a uri string is well-formed
  @staticmethod
  def checkURIIsValid(uri_encoded_str):
    is_valid = None
    try:
      parser_output = URI._getParserOutput(uri_encoded_str)
    except Exception:
      is_valid = False
      return is_valid
    is_valid = True
    return is_valid
  # will always capitalize percent codes
  @staticmethod
  def percentEncode(curr_str, case):
    safe_re = None
    if case == USERINFO_COMPONENT:
      safe_re = USERINFO_SAFE_RE
    elif case == HTTP_USER_COMPONENT:
      safe_re = HTTP_USER_SAFE_RE
    elif case == HTTP_PASSWORD_COMPONENT:
      safe_re = HTTP_PASSWORD_SAFE_RE
    elif case == HOST_COMPONENT:
      safe_re = HOST_SAFE_RE
    elif case == SEGMENT_COMPONENT:
      safe_re = SEGMENT_SAFE_RE
    elif case == PATH_NO_SCHEME_FIRST_SEGMENT_COMPONENT:
      safe_re = PATH_NO_SCHEME_FIRST_SEGMENT_SAFE_RE
    elif case == QUERY_COMPONENT:
      safe_re = QUERY_SAFE_RE
    elif case == HTTP_QUERY_KEY_COMPONENT:
      safe_re = HTTP_QUERY_KEY_SAFE_RE
    elif case == HTTP_QUERY_VALUE_COMPONENT:
      safe_re = HTTP_QUERY_VALUE_SAFE_RE
    elif case == FRAGMENT_COMPONENT:
      safe_re = FRAGMENT_SAFE_RE
    elif case == NOT_A_COMPONENT:
      safe_re = r"(?!.)"
    do_plus_encode = case in {QUERY_COMPONENT, HTTP_QUERY_KEY_COMPONENT, HTTP_QUERY_VALUE_COMPONENT}
    result = URI.percentEncodeHelper(curr_str, safe_re, do_plus_encode)
    return result
  # will always capitalize percent codes
  @staticmethod
  def percentEncodeHelper(curr_str, safe_re, do_plus_encode):
    is_in_ascii = URI.isInASCII(curr_str)	
    if is_in_ascii == False:
      raise Exception()
    chars = list(curr_str)
    regex = re.compile(safe_re)
    words = []
    for char in chars:
      word = None
      if char == " ":
        word = "+"
      elif regex.match(char) == None:
        word = "%" + char.encode("hex").upper()
      else:
        word = char
      words.append(word)
    result = string.join(words, "")
    return result
  @staticmethod
  def percentDecode(curr_str, do_plus_decode, only_decode_encoded_unreserved_chars):
    char_deque = deque(curr_str)
    result_char_deque = deque()
    URI.percentDecodeHelper(char_deque, result_char_deque, do_plus_decode, only_decode_encoded_unreserved_chars)
    result = string.join(result_char_deque, "")
    return result
  @staticmethod
  def percentDecodeHelper(char_deque, result_char_deque, do_plus_decode, only_decode_encoded_unreserved_chars):
    while True:
      num_chars = len(char_deque)
      if num_chars == 0:
        return
      elif num_chars == 1 or num_chars == 2:
        curr_char = char_deque[0]
        char_deque.popleft()
        result_char_deque.append(curr_char)
      else:
        curr_char = char_deque[0]
        next_char = char_deque[1]
        next_next_char = char_deque[2]
        if curr_char == "+" and do_plus_decode == True:
          decoded_char = " "
          char_deque.popleft()
          result_char_deque.append(decoded_char)
          continue
        if curr_char == "%":
          hex_code_str = next_char + next_next_char
          decoded_char = hex_code_str.decode("hex")
          if only_decode_encoded_unreserved_chars == True:
            unreserved_re = uri_parser.UNRESERVED_FRAG_RE
            regex = re.compile(unreserved_re)
            m = regex.match(decoded_char)
            if m != None:
              char_deque.popleft()
              char_deque.popleft()
              char_deque.popleft()
              result_char_deque.append(decoded_char)
              continue
            else:
              curr_char = char_deque.popleft()
              result_char_deque.append(curr_char)
              continue
          else:
            char_deque.popleft()
            char_deque.popleft()
            char_deque.popleft()
            result_char_deque.append(decoded_char)
            continue
        else:
          curr_char = char_deque.popleft()
          result_char_deque.append(curr_char)
          continue
  @staticmethod
  def isInASCII(curr_str):
    chars = list(curr_str)
    candidate_chars = [x for x in chars if not (ord(x) <= 127)]
    num_matching_chars = len(candidate_chars)
    is_in_ascii = num_matching_chars == 0
    return is_in_ascii
  # get HTTP URI version of a URI
  def getHTTPURI(self, is_http_like = False):
    scheme = self.getScheme()
    scheme_str = scheme.getSchemeStr()
    if scheme_str.lower() != "http" and is_http_like == False:
      raise Exception()
    uri_str = self.toString(False, False)
    http_uri = HTTPURI.constructUsingStr(uri_str)
    return http_uri
  def copy(self):
    uri_str = self.toString(False, False)
    next_uri = URI.constructUsingStr(uri_str)
    return next_uri
  def isOfSameType(self, uri):
    return uri.isStandardURI() == True
  def isStandardURI(self):
    return True
  def isHTTPURI(self):
    return False
# can be used for http-like uri's; 
# optional authority has optional userinfo consisting 
# of username and optional password and has optional port, 
# and optional query consists of query parameters
class HTTPURI(URI):
  def __init__(self, scheme, authority, path, query, fragment):
    URI.__init__(self, scheme, authority, path, query, fragment)
  def _createAuthority(self, parser_output):
    self.authority = Authority.constructFromParserOutput(parser_output, True)
  def _createQuery(self, parser_output):
    self.query = HTTPQuery.constructFromParserOutput(parser_output)
  def copy(self):
    uri_str = self.toString(False, False)
    next_uri = HTTPURI.constructUsingStr(uri_str)
    return next_uri
  def getNormalizedQueryString(self):
    return self.getQuery().toString(True)
  def getNonNormalizedQueryString(self):
    return self.getQuery().toString(False)
  def isOfSameType(self, uri):
    return uri.isHTTPURI() == True
  def isStandardURI(self):
    return False
  def isHTTPURI(self):
    return True
  @staticmethod
  def constructUsingStr(uri_str):
    parser_output = URI.constructUsingStrHelper(uri_str)
    http_uri = HTTPURI.constructFromParserOutput(parser_output)
    return http_uri
  @staticmethod
  def constructFromParserOutput(parser_output):
    http_uri = HTTPURI(None, None, None, None, None)
    URI._constructFromParserOutputHelper(parser_output, http_uri)
    return http_uri
class Scheme:
  def __init__(self, scheme_str):
    self.scheme_str = scheme_str
  def setSchemeStr(self, scheme_str):
    self.scheme_str = scheme_str
  def getSchemeStr(self):
    return self.scheme_str
  # perform percent encoding
  def toString(self, do_case_normalize = False):
    result = self.getSchemeStr()
    if do_case_normalize == True:
      result = result.lower()
    return result
  @staticmethod
  def constructFromParserOutput(parser_output):
    if not ("scheme" in parser_output):
      return None
    scheme_str = parser_output["scheme"]
    scheme = Scheme(scheme_str)
    return scheme
  def copy(self):
    scheme_str = self.getSchemeStr()
    scheme = Scheme(scheme_str)
    return scheme
  def isEquivalentTo(self, scheme):
    return self.toString(True) == scheme.toString(True)
class UserInfo:
  def __init__(self, user_info_unencoded_str):
    self.user_info_unencoded_str = user_info_unencoded_str
  def getUserInfoUnencodedStr(self):
    return self.user_info_unencoded_str
  def setUserInfoUnencodedStr(self, user_info_unencoded_str):
    self.user_info_unencoded_str = user_info_unencoded_str
  # perform percent encoding
  def toString(self):
    user_info_unencoded_str = self.getUserInfoUnencodedStr()
    user_info_encoded_str = URI.percentEncode(user_info_unencoded_str, USERINFO_COMPONENT)
    return user_info_encoded_str
  # may return None
  @staticmethod
  def constructFromParserOutput(parser_output):
    if "authority" in parser_output:
      if "userinfo" in parser_output["authority"]:
        user_info_encoded_str = parser_output["authority"]["userinfo"]
        user_info_unencoded_str = URI.percentDecode(user_info_encoded_str, False, False)
        user_info_obj = UserInfo(user_info_unencoded_str)
        return user_info_obj
    return None
  def copy(self):
    user_info_unencoded_str = self.getUserInfoUnencodedStr()
    user_info = UserInfo(user_info_unencoded_str)
    return user_info
  def isEquivalentTo(self, user_info):
    return self.toString() == user_info.toString()
class HTTPUserInfo(UserInfo):
  # password is optional (i.e. it can be None)
  def __init__(self, username_unencoded_str, password_unencoded_str):
    UserInfo.__init__(self, None)
    self.username_unencoded_str = username_unencoded_str
    self.password_unencoded_str = password_unencoded_str
  def havePassword(self):
    return self.password_unencoded_str != None
  def getUserInfoUnencodedStr(self):
    raise Exception()
  def setUserInfoUnencodedStr(self):
    raise Exception()
  def getUsernameUnencodedStr(self):
    return self.username_unencoded_str
  def getPasswordUnencodedStr(self):
    return self.password_unencoded_str
  def setUsernameUnencodedStr(self, username_unencoded_str):
    self.username_unencoded_str = username_unencoded_str
  def setPasswordUnencodedStr(self, password_unencoded_str):
    self.password_unencoded_str = password_unencoded_str
  def getUsernameEncodedStr(self):
    username_unencoded_str = self.getUsernameUnencodedStr()
    username_encoded_str = URI.percentEncode(username_unencoded_str, HTTP_USER_COMPONENT)
    return username_encoded_str
  def getPasswordEncodedStr(self):
    password_unencoded_str = self.getPasswordUnencodedStr()
    if password_unencoded_str == None:
      return None
    password_encoded_str = URI.percentEncode(password_unencoded_str, HTTP_PASSWORD_COMPONENT)
    return password_encoded_str
  # perform percent encoding
  def toString(self):
    username_encoded_str = self.getUsernameEncodedStr()
    password_encoded_str = self.getPasswordEncodedStr()
    result = ""
    result += username_encoded_str
    if self.havePassword() == True:
      result += ":" + password_encoded_str
    return result
  # if password is not present, result password is None
  @staticmethod
  def _breakApartUserInfoEncodedStr(userinfo_encoded_str):
    username_with_optional_password_re = r"(?P<username>[^:]+)(?:(?::(?P<password>[^:]+))?)"
    regex = re.compile(username_with_optional_password_re)
    m = regex.match(userinfo_encoded_str)
    result = None
    if m == None:
      result = (None, None)
    else:
      username_encoded_str = m.group("username")
      password_encoded_str = m.group("password")
      result = (username_encoded_str, password_encoded_str)
    return result
  # may return None
  @staticmethod
  def constructFromParserOutput(parser_output):
    if "authority" in parser_output:
      if "userinfo" in parser_output["authority"]:
        user_info_encoded_str = parser_output["authority"]["userinfo"]
        username_encoded_str, password_encoded_str = HTTPUserInfo._breakApartUserInfoEncodedStr(user_info_encoded_str)
        username_unencoded_str = URI.percentDecode(username_encoded_str, False, False)
        password_unencoded_str = None
        if password_encoded_str != None:
          password_unencoded_str = URI.percentDecode(password_encoded_str, False, False)
        user_info_obj = HTTPUserInfo(username_unencoded_str, password_unencoded_str)
        return user_info_obj
    return None
  def copy(self):
    username_unencoded_str = self.getUsernameUnencodedStr()
    password_unencoded_str = self.getPasswordUnencodedStr()
    http_user_info = HTTPUserInfo(username_unencoded_str, password_unencoded_str)
    return http_user_info
class Authority:
  # user_info_obj, port_int may be None
  def __init__(self, user_info_obj, host_unencoded_str, port_int):
    self.user_info_obj = user_info_obj
    self.host_unencoded_str = host_unencoded_str
    self.port_int = port_int
  def _getUserInfoCopy(self):
    if self.haveUserInfo() == True:
      return self.getUserInfoObj().copy()
    else:
      return None
  def haveUserInfo(self):
    return self.user_info_obj != None
  def setUserInfoObj(self, user_info_obj):
    self.user_info_obj = user_info_obj
  def getUserInfoObj(self):
    return self.user_info_obj
  def getHostUnencodedStr(self):
    return self.host_unencoded_str
  def setHostUnencodedStr(self, host_unencoded_str):
    self.host_unencoded_str = host_unencoded_str
  def getHostEncodedStr(self):
    host_unencoded_str = self.getHostUnencodedStr()
    result = URI.percentEncode(host_unencoded_str, HOST_COMPONENT)
    return result
  def havePortInt(self):
    return self.port_int != None
  def getPortInt(self):
    return self.port_int
  def setPortInt(self, port_int):
    self.port_int = port_int
  # perform percent encoding
  def toString(self, do_case_normalize = False):
    user_info = self.getUserInfoObj()
    host_encoded_str = self.getHostEncodedStr()
    if do_case_normalize == True:
      host_encoded_str = host_encoded_str.lower()
    port_int = self.getPortInt()
    port_str = str(port_int) if port_int != None else None
    value = ""
    if user_info != None:
      user_info_encoded_str = user_info.toString()
      value += user_info_encoded_str + "@"
    value += host_encoded_str
    if port_str != None:
      value += ":" + port_str
    return value
  # may return None
  @staticmethod
  def constructFromParserOutput(parser_output, is_for_http):
    if not ("authority" in parser_output):
      return None
    authority_dict = parser_output["authority"]
    user_info_str = authority_dict["userinfo"] if "userinfo" in authority_dict else None
    host_with_port_str = authority_dict["host_with_port"] if "host_with_port" in authority_dict else None
    host_without_port_str = authority_dict["host_without_port"] if "host_without_port" in authority_dict else None
    host_str = None
    port_int = None
    if host_without_port_str != None:
      host_str = host_without_port_str
    else:
      host_with_port_re = r"(?P<host>[^:]+):(?P<port>[0-9]+)"
      regex = re.compile(host_with_port_re)
      m = regex.match(host_with_port_str)
      host_str = m.group("host")
      port_str = m.group("port")
      port_int = int(port_str)
    host_unencoded_str = URI.percentDecode(host_str, False, False)
    user_info_obj = None
    authority = None
    if is_for_http == True:
      user_info_obj = HTTPUserInfo.constructFromParserOutput(parser_output)
      authority = HTTPAuthority(user_info_obj, host_unencoded_str, port_int)
    else:
      user_info_obj = UserInfo.constructFromParserOutput(parser_output)
      authority = Authority(user_info_obj, host_unencoded_str, port_int)
    return authority
  def copy(self):
    host_unencoded_str = self.getHostUnencodedStr()
    port_int = self.getPortInt()
    next_user_info_obj = self._getUserInfoCopy()
    authority = Authority(next_user_info_obj, host_unencoded_str, port_int)
    return authority
  def isEquivalentTo(self, authority):
    return self.toString(True) == authority.toString(True)
  def getForHTTPURI(self):
    uri_str = self.toString(False)
    authority_dict = {}
    if self.haveUserInfo() == True:
      user_info_obj = self.getUserInfoObj()
      user_info_str = user_info_obj.toString()
      authority_dict["userinfo"] = user_info_str
    if self.havePortInt() == True:
      port_int = self.getPortInt()
      host_with_port_str = self.getHostEncodedStr() + ":" + str(port_int)
      authority_dict["host_with_port"] = host_with_port_str
    else:
      host_without_port_str = self.getHostEncodedStr()
      authority_dict["host_without_port"] = host_without_port_str
    parser_output = {"authority": authority_dict}
    http_authority = Authority.constructFromParserOutput(parser_output, True)
    return http_authority
# override some of Authority's methods to keep backwards-compatibility
class HTTPAuthority(Authority):
  suffix_list = PublicSuffixList()
  def __init__(self, user_info_obj, host_str, port_int):
    Authority.__init__(self, user_info_obj, host_str, port_int)
  def getDomainUnencoded(self):
    host_unencoded_str = self.getHostUnencodedStr()
    is_ip_address = HTTPAuthority._isIPAddress(host_unencoded_str)
    result = None
    if is_ip_address == False:
      result = HTTPAuthority.suffix_list.get_public_suffix(host_unencoded_str)
    return result
  @staticmethod
  def _isIPAddress(host_unencoded_str):
    IPV4ADDRESS_RE = uri_parser.IPV4ADDRESS_FRAG_RE
    IP_LITERAL_RE = uri_parser.IP_LITERAL_FRAG_RE
    IP_ADDRESS_RE = r"^(?:(?:" + IPV4ADDRESS_RE + r")|(?:" + IP_LITERAL_RE + r"))$"
    regex = re.compile(IP_ADDRESS_RE)
    m = regex.match(host_unencoded_str)
    is_ip_address = m != None
    return is_ip_address
  def copy(self):
    host_unencoded_str = self.getHostUnencodedStr()
    port_int = self.getPortInt()
    next_user_info_obj = self._getUserInfoCopy()
    http_authority = HTTPAuthority(next_user_info_obj, host_unencoded_str, port_int)
    return http_authority
# starts with a '/'
ABSOLUTE = 0
# does not start with a '/'
RELATIVE = 1
class Path:
  def __init__(self, segment_unencoded_str_list, path_type, ends_in_ts):
    self.segment_unencoded_str_list = segment_unencoded_str_list
    self.path_type = path_type
    self.ends_in_ts = ends_in_ts
  def getEndsInTrailingSlash(self):
    return self.ends_in_ts
  def setEndsInTrailingSlash(self, ends_in_ts):
    self.ends_in_ts = ends_in_ts
  def haveSegments(self):
    return len(self.getSegmentUnencodedStrList()) != 0
  def getSegmentUnencodedStrList(self):
    return self.segment_unencoded_str_list
  # takes O(n) time
  # reason why we care about scheme existence is that we need to possibly percent-encode colons for first segment
  def getSegmentEncodedStrList(self, have_scheme):
    segment_unencoded_str_list = self.getSegmentUnencodedStrList()
    path_type = self.getPathType()
    case = None
    result = None
    if have_scheme == False and path_type == RELATIVE:
      first_segment = segment_unencoded_str_list[0]
      remaining_segments = segment_unencoded_str_list[1 : ]
      first_result = URI.percentEncode(first_segment, PATH_NO_SCHEME_FIRST_SEGMENT_COMPONENT)
      remaining_result = [URI.percentEncode(x, SEGMENT_COMPONENT) for x in remaining_segments]
      result = [first_result] + remaining_result
    else:
      result = [URI.percentEncode(x, SEGMENT_COMPONENT) for x in segment_unencoded_str_list]
    return result
  def getPathType(self):
    return self.path_type
  # perform percent encoding
  # reason why we care about scheme existence is that we need to possibly percent-encode colons for first segment
  def toString(self, have_scheme):
    segment_encoded_str_list = self.getSegmentEncodedStrList(have_scheme)
    path_type = self.getPathType()
    value = ""
    segment_str = string.join(segment_encoded_str_list, "/")
    if path_type == RELATIVE or self.haveSegments() == False:
      pass
    elif path_type == ABSOLUTE and self.haveSegments() == True:
      value += "/"
    value += segment_str
    if self.getEndsInTrailingSlash() == True:
      value += "/"
    return value
  @staticmethod
  def constructFromParserOutput(parser_output):
    path_dict = parser_output["path"]
    path_type_str = path_dict["type"]
    segment_encoded_str_list = path_dict["segments"]
    ends_in_ts = path_dict["ends_in_ts"]
    segment_unencoded_str_list = [URI.percentDecode(x, False, False) for x in segment_encoded_str_list]
    path_type = None
    if path_type_str == "absolute":
      path_type = ABSOLUTE
    elif path_type_str == "relative":
      path_type = RELATIVE
    path = Path(segment_unencoded_str_list, path_type, ends_in_ts)
    return path
  def copy(self):
    segment_unencoded_str_list = self.getSegmentUnencodedStrList()
    next_segment_unencoded_str_list = segment_unencoded_str_list[ : ]
    path_type = self.getPathType()
    ends_in_ts = self.getEndsInTrailingSlash()
    path = Path(next_segment_unencoded_str_list, path_type, ends_in_ts)
    return path
  def _setSegmentUnencodedStrList(self, segment_unencoded_str_list):
    self.segment_unencoded_str_list = segment_unencoded_str_list
  def removeDotSegmentsAndUpdateTrailingSlashStatus(self):
    have_trailing_slash = self.removeDotSegments()
    if have_trailing_slash == True:
      self.setEndsInTrailingSlash(True)
  # returns a flag saying whether we ended in a dot segment
  def removeDotSegments(self):
    segment_unencoded_str_list = self.getSegmentUnencodedStrList()
    ended_in_dot_segment = None
    num_segments = len(segment_unencoded_str_list)
    if num_segments == 0:
      ended_in_dot_segment = False
    else:
      last_segment = segment_unencoded_str_list[num_segments - 1]
      ended_in_dot_segment = last_segment == "." or last_segment == ".."
    next_segment_list = segment_unencoded_str_list
    next_next_segment_list = [x for x in next_segment_list if x != "."]
    result_segment_list = Path._removeDoubleDotSegments(next_next_segment_list)
    self._setSegmentUnencodedStrList(result_segment_list)
    return ended_in_dot_segment
  @staticmethod
  def _removeDoubleDotSegments(unencoded_segment_list):
    unencoded_segment_deque = deque(unencoded_segment_list)
    result_deque = deque()
    Path._removeDoubleDotSegmentsHelper(result_deque, unencoded_segment_deque)
    result_list = list(result_deque)
    return result_list
  @staticmethod
  def _removeDoubleDotSegmentsHelper(result_deque, unencoded_segment_deque):
    while True:
      if len(unencoded_segment_deque) == 0:
        return
      curr_segment = unencoded_segment_deque.popleft()
      if curr_segment == "..":
        if len(result_deque) != 0:
          removed_segment = result_deque.pop()
        else:
          pass
      else:
        result_deque.append(curr_segment)
      continue
  # remove segment from end
  def popSegment(self):
    segment_unencoded_str_list = self.segment_unencoded_str_list
    segment_unencoded_str = segment_unencoded_str_list.pop()
    return segment_unencoded_str
  # add segment to end
  def pushSegment(self, segment_unencoded_str):
    segment_unencoded_str_list = self.segment_unencoded_str_list
    segment_unencoded_str_list.append(segment_unencoded_str)
  # change directory
  # ends_in_directory refers to current path
  def chdir(self, directory_unencoded_str, ends_in_directory):
    if self.haveSegments() == True:
      if ends_in_directory == False:
        self.popSegment()
    self.pushSegment(directory_unencoded_str)
  def isEquivalentTo(self, path):
    segments1 = self.getSegmentUnencodedStrList()
    segments2 = path.getSegmentUnencodedStrList()
    are_equivalent = True
    if len(segments1) == len(segments2):
      for i in xrange(len(segments1)):
        segment1 = segments1[i]
        segment2 = segments2[i]
        if segment1 != segment2:
          are_equivalent = False
          break
    else:
      are_equivalent = False
    path_type1 = self.getPathType()
    path_type2 = path.getPathType()
    if path_type1 != path_type2:
      are_equivalent = False
    return are_equivalent
class Query:
  def __init__(self, query_unencoded_str):
    self.query_unencoded_str = query_unencoded_str
  def isHTTPQuery(self):
    return False
  def getQueryUnencodedStr(self):
    return self.query_unencoded_str
  def setQueryUnencodedStr(self, query_unencoded_str):
    self.query_unencoded_str = query_unencoded_str
  def getQueryEncodedStr(self):
    query_unencoded_str = self.getQueryUnencodedStr()
    result = URI.percentEncode(query_unencoded_str, QUERY_COMPONENT)
    return result
  # perform percent encoding
  def toString(self):
    query_encoded_str = self.getQueryEncodedStr()
    return query_encoded_str
  # may return None
  @staticmethod
  def constructFromParserOutput(parser_output, is_for_http):
    if not ("query" in parser_output):
      return None
    query_encoded_str = parser_output["query"]
    query = None
    if is_for_http == True:
      query = HTTPQuery.constructFromParserOutput(parser_output)
    else:
      query_unencoded_str = URI.percentDecode(query_encoded_str, True, False)
      query = Query(query_unencoded_str)
    return query
  def copy(self):
    query_unencoded_str = self.getQueryUnencodedStr()
    query = Query(query_unencoded_str)
    return query
  def isEquivalentTo(self, query):
    return self.toString() == query.toString()
  def getForHTTPURI(self):
    uri_str = self.toString()
    parser_output = {"query": uri_str}
    http_query = HTTPQuery.constructFromParserOutput(parser_output)
    return http_query
class HTTPQuery(Query):
  def __init__(self, unencoded_key_value_pair_list, unencoded_singleton_value_list):
    Query.__init__(self, None)
    self.unencoded_key_to_value_list_dict = defaultdict(lambda: [])
    for unencoded_key_value_pair in unencoded_key_value_pair_list:
      unencoded_key, unencoded_value = unencoded_key_value_pair
      self.addUnencodedQueryKeyValuePair(unencoded_key, unencoded_value)
    self.unencoded_singleton_to_count_dict = defaultdict(lambda: 0)
    for unencoded_singleton_value in unencoded_singleton_value_list:
      self.addUnencodedSingletonValue(unencoded_singleton_value)
  def isHTTPQuery(self):
    return True
  def getQueryUnencodedStr(self):
    raise Exception()
  def setQueryUnencodedStr(self, query_unencoded_str):
    raise Exception()
  def getQueryEncodedStr(self):
    raise Exception()
  def _getUnencodedKeyToValueListDict(self):
    return self.unencoded_key_to_value_list_dict
  def _getUnencodedSingletonToCountDict(self):
    return self.unencoded_singleton_to_count_dict
  def getUnencodedQueryKeyValuePairs(self, do_query_parameter_sorting):
    unencoded_key_to_value_list_dict = self._getUnencodedKeyToValueListDict()
    key_to_value_list_pair_list = unencoded_key_to_value_list_dict.items()
    pair_list = []
    for key_to_value_list_pair in key_to_value_list_pair_list:
      key, value_list = key_to_value_list_pair
      for value in value_list:
        pair = (key, value)
        pair_list.append(pair)
    if do_query_parameter_sorting == True:
      pair_list.sort()
    result = pair_list
    return result
  def addUnencodedQueryKeyValuePair(self, key_unencoded_str, value_unencoded_str):
    unencoded_key_to_value_list_dict = self._getUnencodedKeyToValueListDict()
    unencoded_key_to_value_list_dict[key_unencoded_str].append(value_unencoded_str)
  def removeUnencodedQueryKeyValuePair(self, key_unencoded_str, value_unencoded_str):
    unencoded_key_to_value_list_dict = self._getUnencodedKeyToValueListDict()
    unencoded_key_to_value_list_dict[key_unencoded_str].remove(value_encoded_str)
  def getUnencodedSingletonValueList(self, do_query_parameter_sorting):
    unencoded_singleton_to_count_dict = self._getUnencodedSingletonToCountDict()
    values = []
    for unencoded_key in unencoded_singleton_to_count_dict.keys():
      count = unencoded_singleton_to_count_dict[unencoded_key]
      curr_values = [unencoded_key] * count
      values.extend(curr_values)
    if do_query_parameter_sorting == True:
      values.sort()
    result = values
    return result
  def addUnencodedSingletonValue(self, unencoded_singleton_str):
    unencoded_singleton_to_count_dict = self._getUnencodedSingletonToCountDict()
    unencoded_singleton_to_count_dict[unencoded_singleton_str] += 1
  def removeUnencodedSingletonValue(self, unencoded_singleton_str):
    unencoded_singleton_to_count_dict = self._getUnencodedSingletonToCountDict()
    unencoded_singleton_to_count_dict[unencoded_singleton_str] -= 1
  # perform percent encoding
  # lexicographic ordering of parameters, favoring having all singletons on left
  def toString(self, do_query_parameter_sorting = False):
    unencoded_key_value_pairs = self.getUnencodedQueryKeyValuePairs(do_query_parameter_sorting)
    unencoded_singleton_value_list = self.getUnencodedSingletonValueList(do_query_parameter_sorting)
    str_list = []
    for unencoded_singleton_value in unencoded_singleton_value_list:
      curr_str = unencoded_singleton_value
      next_str = URI.percentEncode(curr_str, HTTP_QUERY_KEY_COMPONENT)
      str_list.append(next_str)
    for unencoded_key_value_pair in unencoded_key_value_pairs:
      unencoded_key, unencoded_value = unencoded_key_value_pair
      encoded_key = URI.percentEncode(unencoded_key, HTTP_QUERY_KEY_COMPONENT)
      encoded_value = URI.percentEncode(unencoded_value, HTTP_QUERY_VALUE_COMPONENT)
      curr_str = encoded_key + "=" + encoded_value
      str_list.append(curr_str)
    result = string.join(str_list, "&")
    return result
  # may return None
  @staticmethod
  def constructFromParserOutput(parser_output):
    if not ("query" in parser_output):
      return None
    query_encoded_str = parser_output["query"]
    key_value_str_list = query_encoded_str.split("&")
    key_value_pair_list = []
    singleton_values = []
    for key_value_str in key_value_str_list:
      if '=' not in key_value_str:
        singleton_encoded_value = key_value_str
        singleton_unencoded_value = URI.percentDecode(singleton_encoded_value, False, False)
        singleton_values.append(singleton_unencoded_value)
      else:
        str_list = key_value_str.split("=")
        key_encoded_str = str_list[0]
        value_encoded_str = str_list[1]
        key_unencoded_str = URI.percentDecode(key_encoded_str, False, False)
        value_unencoded_str = URI.percentDecode(value_encoded_str, False, False)
        pair = (key_unencoded_str, value_unencoded_str)
        key_value_pair_list.append(pair)
    query = HTTPQuery(key_value_pair_list, singleton_values)
    return query
  def copy(self):
    unencoded_key_value_pair_list = self.getUnencodedQueryKeyValuePairs()
    unencoded_singleton_value_list = self.getUnencodedSingletonValueList()
    http_query = HTTPQuery(unencoded_key_value_pair_list, unencoded_singleton_value_list)
    return http_query
  def isEquivalentTo(self, query):
    return self.toString(True) == query.toString(True)
class Fragment:
  def __init__(self, fragment_unencoded_str):
    self.fragment_unencoded_str = fragment_unencoded_str
  def getFragmentUnencodedStr(self):
    return self.fragment_unencoded_str
  def setFragmentUnencodedStr(self, fragment_unencoded_str):
    self.fragment_unencoded_str = fragment_unencoded_str
  def getFragmentEncodedStr(self):
    fragment_unencoded_str = self.getFragmentUnencodedStr()
    result = URI.percentEncode(fragment_unencoded_str, FRAGMENT_COMPONENT)
    return result
  # perform percent encoding
  def toString(self):
    fragment_str = self.getFragmentEncodedStr()
    return fragment_str
  # may return None
  @staticmethod
  def constructFromParserOutput(parser_output):
    if not ("frag" in parser_output):
      return None
    fragment_str = parser_output["frag"]
    fragment = Fragment(fragment_str)
    return fragment
  def copy(self):
    fragment_unencoded_str = self.getFragmentUnencodedStr()
    fragment = Fragment(fragment_unencoded_str)
    return fragment
  def isEquivalentTo(self, fragment):
    return self.toString() == fragment.toString()
def main():
  stream = sys.stdin
  line = stream.readline()
  line = line.rstrip("\n")
  http_uri = HTTPURI(line)
  print http_uri.toString(True, True)
if __name__ == "__main__":
  main()
