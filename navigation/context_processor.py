
def get_nav_dictionary(request):
  navigation_list = [
      { 'href':'/', 'name':'Home' },
      { 'href':'/how-it-works/', 'name':'How It Works' },
      { 'href':'/examples/', 'name':'Examples' },
      { 'href':'/faq/', 'name':'FAQ' },
      { 'href':'/contact-us/', 'name':'Contact Us' },
      { 'href':'/blog/', 'name':'Blog' },
      { 'href':'/photoshoppers/', 'name':'For Photoshoppers' },
  ]

  for nav_entry in navigation_list:
    if nav_entry['href'] == request.path:
      nav_entry['current'] = True
    else:
      nav_entry['current'] = False
  return locals()

