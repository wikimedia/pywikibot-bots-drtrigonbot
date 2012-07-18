Installation:
  pip install path/to/py_w3c - it is not in the pypi right now.

Usage:
  1. As library - 

    # import HTML validator
    from py_w3c.validators.html.validator import HTMLValidator

    # create validator instance
    vld = HTMLValidator()

    # validate
    vld.validate("http://datetostr.org")

    # look for errors
    print vld.errors  # list with dicts

    # look for warnings
    print vld.warnings

  There are 3 methods of validating:
    1. validate url - HTMLValidator().validate(url)
    2. validate file - HTMLValidator().validate_file(file_name_or_content)
    3. validate fragment - HTMLValidator().validate_fragment(fragment_string)

  You can pass charset or doctype while creating validator instance. This will force validator to use passed doctype or charset for validation.
    Example.
      vld = HTMLValidator(doctype="XHTML1", charset="utf-8")

      # now validator uses XHTML1 doctype and utf-8 charset ignoring doctype and charset in the document content
      vld.validate("http://datetostr.org")

  2. As standalone script - (not very usefull right now)
    Now only url validating is allowed for standalone script.
    w3c_validate http://datetostr.org
    Prints warnings and errors to the console.
