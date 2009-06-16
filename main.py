#!/usr/bin/env python

import cgi
import os
import time
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

def parse_length_string(str):
  unit_multipliers = {
    'second': 1,
    'minute': 60,
    'hour':   3600,
    'day':    86400,
    'week':   604800,
    'month':  2592000,
    'year':   31536000,
    'decade': 315360000
  }
  try:
    num, unit = str.split()
    num = int(num)
    unit = unit.rstrip('s')
  except:
    return None
    
  if unit in unit_multipliers:
    return num * unit_multipliers[unit]
  else:
    return None

class MainPage(webapp.RequestHandler):
  num_rras = 5
  default_xff = 0.5
  default_step = 60
  
  def templateData(self):
    data = {
      'rras': [],
      'step': self.default_step,
      'xff': self.default_xff,
      'rra_code': None,
    }
    for i in range(1, self.num_rras+1):
      data['rras'].append({
        'num': i,
        'step': '',
        'length': '',
      })
    return data
  
  def get(self):
    data = self.templateData()
    self.render(data)

  def post(self):
    data     = self.templateData()
    type     = 'AVERAGE'
    rra_code = []
    now      = time.time()
    try:
      step = int(cgi.escape(self.request.get('step')))
    except:
      step = self.default_step
    try:
      xff = float(cgi.escape(self.request.get('xff')))
    except:
      xff = self.default_xff

    # sent submitted data back to template
    data['step'] = step
    data['xff']  = xff

    # generate code
    for i in range(1, self.num_rras+1):
      rra_step   = cgi.escape(self.request.get('rra_%d_step' % i))
      rra_length = cgi.escape(self.request.get('rra_%d_length' % i))
      
      data['rras'][i-1]['step'] = rra_step
      data['rras'][i-1]['length'] = rra_length
      
      rra_step_secs   = parse_length_string(rra_step)
      rra_length_secs = parse_length_string(rra_length)
      
      if rra_step_secs and rra_length_secs:
        steps_per   = rra_step_secs / step
        steps_total = rra_length_secs / step
        rows        = steps_total / steps_per
        rra_code.append('RRA:%s:%s:%s:%s' % (type, xff, steps_per, rows))

    data['rra_code'] = "\n".join(rra_code)
      
    self.render(data)

  def render(self, data):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, data))

application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
