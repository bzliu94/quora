# 2016-04-25

# many tests taken out of rfc 3986

import unittest
from python_uri import URI, HTTPURI, Scheme, Authority, Path, Query, Fragment, HTTPAuthority, HTTPQuery, UserInfo, HTTPUserInfo, ABSOLUTE, RELATIVE, HOST_COMPONENT, HTTP_QUERY_KEY_COMPONENT, QUERY_COMPONENT, NOT_A_COMPONENT
def getComponentStrTuple(line, is_http_like = False, do_normalize = False):
  uri = None
  if is_http_like == True:
    uri = HTTPURI.constructUsingStr(line)
  else:
    uri = URI.constructUsingStr(line)
  components = uri.getComponents()
  scheme, authority, path, query, fragment = components
  scheme_str = scheme.toString(do_normalize) if scheme != None else None
  authority_str = authority.toString(do_normalize) if authority != None else None
  have_scheme = uri.haveScheme()
  if do_normalize == True:
    path.removeDotSegments()
  path_str = path.toString(have_scheme) if path != None else None
  query_str = None
  if query != None:
    if query.isHTTPQuery() == True:
      query_str = query.toString(do_normalize)
    else:
      query_str = query.toString()
  fragment_str = fragment.toString() if fragment != None else None
  component_str_tuple = (scheme_str, authority_str, path_str, query_str, fragment_str)
  return component_str_tuple
def getRRResult(base_URI_str, relative_URI_str, is_strict = False):
  relative_URI = URI.constructUsingStr(relative_URI_str)
  base_URI = HTTPURI.constructUsingStr(base_URI_str)
  result_URI = relative_URI.resolve(base_URI, is_strict)
  result = result_URI.toNormalizedString()
  return result
class TestURI(unittest.TestCase):
  def setUp(self):
    pass
  def testComponents(self):
    line = "http://www.hello.com/hello1/hello2/?hello#hello"
    component_str_tuple = getComponentStrTuple(line, True)
    self.assertEqual(component_str_tuple, ("http", "www.hello.com", "/hello1/hello2/", "hello", "hello"))
    line = "ftp://ftp.is.co.za/rfc/rfc1808.txt"
    component_str_tuple = getComponentStrTuple(line, False)
    self.assertEqual(component_str_tuple, ("ftp", "ftp.is.co.za", "/rfc/rfc1808.txt", None, None))
    line = "http://www.ietf.org/rfc/rfc2396.txt"
    component_str_tuple = getComponentStrTuple(line, True)
    self.assertEqual(component_str_tuple, ("http", "www.ietf.org", "/rfc/rfc2396.txt", None, None))
    line = "ldap://[2001:db8::7]/c=GB?objectClass?one"
    component_str_tuple = getComponentStrTuple(line, True)
    self.assertEqual(component_str_tuple, ("ldap", "[2001:db8::7]", "/c=GB", "objectClass?one", None))
    line = "mailto:John.Doe@example.com"
    component_str_tuple = getComponentStrTuple(line, False)
    self.assertEqual(component_str_tuple, ("mailto", None, "John.Doe@example.com", None, None))
    line = "news:comp.infosystems.www.servers.unix"
    component_str_tuple = getComponentStrTuple(line, False)
    self.assertEqual(component_str_tuple, ("news", None, "comp.infosystems.www.servers.unix", None, None))
    line = "tel:+1-816-555-1212"
    component_str_tuple = getComponentStrTuple(line, False)
    self.assertEqual(component_str_tuple, ("tel", None, "+1-816-555-1212", None, None))
    line = "telnet://192.0.2.16:80/"
    component_str_tuple = getComponentStrTuple(line, False)
    self.assertEqual(component_str_tuple, ("telnet", "192.0.2.16:80", "/", None, None))
    line = "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"
    component_str_tuple = getComponentStrTuple(line, False)
    self.assertEqual(component_str_tuple, ("urn", None, "oasis:names:specification:docbook:dtd:xml:4.1.2", None, None))
  def testNormalization(self):
    line = "hTtP://wWw.hEllo.coM/hello1/hello2/%2f/?there&hello&b=2&a=1#hello"
    uri = HTTPURI.constructUsingStr(line)
    result = uri.toNormalizedString()
    self.assertEqual(result, "http://www.hello.com/hello1/hello2/%2F/?hello&there&a=1&b=2#hello")
  def testComparison(self):
    line1 = "example://a/b/c/%7Bfoo%7D"
    uri1 = URI.constructUsingStr(line1)
    line2 = "eXAMPLE://a/./b/../b/%63/%7bfoo%7d"
    uri2 = URI.constructUsingStr(line2)
    self.assertTrue(uri1.isEquivalentTo(uri2))
    line1 = "http://a/b/c/%7Bfoo%7D"
    uri1 = URI.constructUsingStr(line1)
    line2 = "hTTP://a/./b/../b/%63/%7bfoo%7d"
    uri2 = URI.constructUsingStr(line2)
    self.assertTrue(uri1.isEquivalentTo(uri2))
    line1 = "http://www.hello.com/"
    uri1 = URI.constructUsingStr(line1)
    line2 = "http://www.there.com/"
    uri2 = URI.constructUsingStr(line2)
    self.assertFalse(uri1.isEquivalentTo(uri2))
  def testChDir(self):
    line = "http://www.hello.com/"
    uri = URI.constructUsingStr(line)
    path = uri.getPath()
    path.chdir("there", True)
    self.assertEqual(uri.toString(), "http://www.hello.com/there/")
  def testQueryParameters(self):
    line = "http://www.hello.com/hello1/hello2/?hello&there&b=2&a=1#hello"
    uri = HTTPURI.constructUsingStr(line)
    query = uri.getQuery()
    key_value_pairs = query.getUnencodedQueryKeyValuePairs(True)
    self.assertEqual(len(key_value_pairs), 2)
    self.assertEqual(key_value_pairs[0], ("a", "1"))
    self.assertEqual(key_value_pairs[1], ("b", "2"))
  def testQuerySingletons(self):
    line = "http://www.hello.com/hello1/hello2/?hi&hello&a=1&b=2#hello"
    uri = HTTPURI.constructUsingStr(line)
    query = uri.getQuery()
    singleton_list = query.getUnencodedSingletonValueList(True)
    self.assertEqual(len(singleton_list), 2)
    self.assertEqual(singleton_list[0], "hello")
    self.assertEqual(singleton_list[1], "hi")
  def testSwapOutComponent(self):
    line = "http://www.hello.com/hello1/hello2/?hello&there&a=1&b=2#hello"
    uri = HTTPURI.constructUsingStr(line)
    user_info = HTTPUserInfo("user", "password")
    authority = HTTPAuthority(user_info, "www.there.com", 80)
    uri.setAuthority(authority)
    result_str = uri.toNormalizedString()
    self.assertEqual(result_str, "http://user:password@www.there.com:80/hello1/hello2/?hello&there&a=1&b=2#hello")
    line = "ftp://ftp.is.co.za/rfc/rfc1808.txt"
    uri = URI.constructUsingStr(line)
    user_info = UserInfo("jane_doe")
    authority = uri.getAuthority()
    authority.setUserInfoObj(user_info)
    result_str = uri.toNormalizedString()
    self.assertEqual(result_str, "ftp://jane_doe@ftp.is.co.za/rfc/rfc1808.txt")
    line = "http://www.hello.com/hello1/hello2/?hello=there#hello"
    uri = HTTPURI.constructUsingStr(line)
    user_info = HTTPUserInfo("user", None)
    uri.getAuthority().setUserInfoObj(user_info)
    result_str = uri.toNormalizedString()
    self.assertEqual(result_str, "http://user@www.hello.com/hello1/hello2/?hello=there#hello")
    line = "http://abc@www.hello.com/hello1/hello2/?hello=there#hello"
    uri = URI.constructUsingStr(line)
    uri.getAuthority().setUserInfoObj(None)
    result_str = uri.toNormalizedString()
    self.assertEqual(result_str, "http://www.hello.com/hello1/hello2/?hello=there#hello")
  def testManualURICreation(self):
    scheme = Scheme("http")
    user_info = HTTPUserInfo("user", None)
    host = "www.hello.com"
    port = 80
    authority = HTTPAuthority(user_info, host, port)
    path = Path(["hello1", "hello2"], ABSOLUTE, True)
    query = HTTPQuery([("a", "1"), ("b", "2")], ["hello", "there"])
    fragment = Fragment("hello")
    http_uri = HTTPURI(scheme, authority, path, query, fragment)
    result_str = http_uri.toNormalizedString()
    self.assertEqual(result_str, "http://user@www.hello.com:80/hello1/hello2/?hello&there&a=1&b=2#hello")
  def testPercentEncode(self):
    line = "hi, +-%"
    result_str = URI.percentEncode(line, NOT_A_COMPONENT)
    self.assertEqual(result_str, "%68%69%2C+%2B%2D%25")
  def testPercentDecode(self):
    line = "%68%69%2C+%2B%2D%25"
    result_str1 = URI.percentDecode(line, True, False)
    self.assertEqual(result_str1, "hi, +-%")
    result_str2 = URI.percentDecode(line, True, True)
    self.assertEqual(result_str2, "hi%2C %2B-%25")
  def testGetDomain(self):
    line = "http://www.hello.com/hello1/hello2/?hello#hello"
    uri = HTTPURI.constructUsingStr(line)
    authority = uri.getAuthority()
    domain_str = authority.getDomainUnencoded()
    self.assertEqual(domain_str, "hello.com")
  def testComponentPercentCoding(self):
    result1 = URI.percentEncode("www./.com", HOST_COMPONENT)
    self.assertEqual(result1, "www.%2F.com")
    result2 = URI.percentEncode("a&b", HTTP_QUERY_KEY_COMPONENT)
    self.assertEqual(result2, "a%26b")
    result3 = URI.percentEncode("a=b+2&b=hello there + bye", QUERY_COMPONENT)
    self.assertEqual(result3, "a=b%2B2&b=hello+there+%2B+bye")
    encoded_str1 = "www.%2F.com"
    result1 = URI.percentDecode(encoded_str1, True, False)
    self.assertEqual(result1, "www./.com")
    encoded_str2 = "a%26b"
    result2 = URI.percentDecode(encoded_str2, True, False)
    self.assertEqual(result2, "a&b")
    encoded_str3 = "a=b%2B2&b=hello+there+%2B+bye"
    result3 = URI.percentDecode(encoded_str3, True, False)
    self.assertEqual(result3, "a=b+2&b=hello there + bye")
  def testHTTPURI(self):
    # test username, password, port
    line = "http://www.hello.com/hello1/hello2/?hello&there&a=1&b=2#hello"
    uri = HTTPURI.constructUsingStr(line)
    http_authority = uri.getAuthority()
    http_user_info = HTTPUserInfo("person:frog", "sharpener^eraser")
    http_authority.setPortInt(80)
    http_authority.setUserInfoObj(http_user_info)
    result_str = uri.toNormalizedString()
    self.assertEqual(result_str, "http://person%3Afrog:sharpener%5Eeraser@www.hello.com:80/hello1/hello2/?hello&there&a=1&b=2#hello")
    self.assertEqual(http_authority.getPortInt(), 80)
    self.assertEqual(http_user_info.getUsernameUnencodedStr(), "person:frog")
    self.assertEqual(http_user_info.getPasswordUnencodedStr(), "sharpener^eraser")
  def testIPAddressIdentification(self):
    # also check with userinfo and port
    host_str1 = "192.168.0.1"
    result1 = HTTPAuthority._isIPAddress(host_str1)
    self.assertTrue(result1)
    host_str2 = "[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]"
    result2 = HTTPAuthority._isIPAddress(host_str2)
    self.assertTrue(result2)
    host_str3 = "[vFE.a-!:]"
    result3 = HTTPAuthority._isIPAddress(host_str3)
    self.assertTrue(result3)
    host_str4 = "hello.com"
    result4 = HTTPAuthority._isIPAddress(host_str4)
    self.assertFalse(result4)
  def testRemoveDotSegments(self):
    uri_str1 = "ftp://ftp.hello.com/a/b/c/../d"
    uri1 = URI.constructUsingStr(uri_str1)
    result1 = uri1.toNormalizedString()
    self.assertEqual(result1, "ftp://ftp.hello.com/a/b/d")
    uri_str2 = "http://www.hello.com/a/b/c/.././../d/../e/f"
    uri2 = HTTPURI.constructUsingStr(uri_str2)
    result2 = uri2.toNormalizedString()
    self.assertEqual(result2, "http://www.hello.com/a/e/f")
    uri_str3 = "http://www.hello.com/a/b/c/."
    uri3 = HTTPURI.constructUsingStr(uri_str3)
    result3 = uri3.toNormalizedString()
    self.assertEqual(result3, "http://www.hello.com/a/b/c/")
  def testRelativeResolution(self):
    base_URI_str_a = "http://hello.com/#hello"
    result1 = getRRResult(base_URI_str_a, "/a/b/c/./../../g")
    self.assertEqual(result1, "http://hello.com/a/g")
    result2 = getRRResult(base_URI_str_a, "mid/content=5/../6")
    self.assertEqual(result2, "http://hello.com/mid/6")
    base_URI_str_b = "http://a/b/c/d;p?q"
    result3 = getRRResult(base_URI_str_b, "g:h")
    self.assertEqual(result3, "g:h")
    result4 = getRRResult(base_URI_str_b, "g")
    self.assertEqual(result4, "http://a/b/c/g")
    tests = [("g:h", "g:h"), 
	("g", "http://a/b/c/g"), 
	("./g", "http://a/b/c/g"), 
	("g/", "http://a/b/c/g/"), 
	("/g", "http://a/g"), 
	("//g", "http://g"), 
	("?y", "http://a/b/c/d;p?y"), 
	("g?y", "http://a/b/c/g?y"), 
	("#s", "http://a/b/c/d;p?q#s"), 
	("g#s", "http://a/b/c/g#s"), 
	("g?y#s", "http://a/b/c/g?y#s"), 
	(";x", "http://a/b/c/;x"), 
	("g;x", "http://a/b/c/g;x"), 
	("g;x?y#s", "http://a/b/c/g;x?y#s"), 
	("", "http://a/b/c/d;p?q"), 
	(".", "http://a/b/c/"), 
	("./", "http://a/b/c/"), 
	("..", "http://a/b/"), 
	("../", "http://a/b/"), 
	("../g", "http://a/b/g"), 
	("../..", "http://a/"), 
	("../../", "http://a/"), 
	("../../g", "http://a/g"), 
	("../../../g", "http://a/g"), 
	("../../../../g", "http://a/g"), 
	("/./g", "http://a/g"), 
	("/../g", "http://a/g"), 
	("g.", "http://a/b/c/g."), 
	(".g", "http://a/b/c/.g"), 
	("g..", "http://a/b/c/g.."), 
	("..g", "http://a/b/c/..g"), 
	("./../g" , "http://a/b/g"), 
	("./g/.", "http://a/b/c/g/"), 
	("g/./h", "http://a/b/c/g/h"), 
	("g/../h" , "http://a/b/c/h"), 
	("g;x=1/./y", "http://a/b/c/g;x=1/y"), 
	("g;x=1/../y", "http://a/b/c/y"), 
	("g?y/./x", "http://a/b/c/g?y/./x"), 
	("g?y/../x", "http://a/b/c/g?y/../x"), 
	("g#s/./x", "http://a/b/c/g#s/./x"), 
	("g#s/../x", "http://a/b/c/g#s/../x")]
    for test_tuple in tests:
      # print test_tuple
      relative_reference_str, target_str = test_tuple
      result = getRRResult(base_URI_str_b, relative_reference_str)
      self.assertEqual(result, target_str)
    # for strict parsers
    result5 = getRRResult(base_URI_str_b, "http:g", True)
    self.assertEqual(result5, "http:g")
    # for backward compatibility
    result6 = getRRResult(base_URI_str_b, "http:g", False)
    self.assertEqual(result6, "http://a/b/c/g")
if __name__ == "__main__":
    unittest.main()
