# -*- coding: utf-8 -*-
import os, yaml, uuid, csv
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_zurb_foundation import Foundation

#from Crypto.Hash import SHA256
#from Crypto.Cipher import AES

app = Flask(__name__)

Foundation(app)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    SECRET_CBC='',
    USERNAME='admin',
    #PASSWORD='\x8civ\xe5\xb5A\x04\x15\xbd\xe9\x08\xbdM\xee\x15\xdf\xb1g\xa9\xc8s\xfcK\xb8\xa8\x1fo*\xb4H\xa9\x18'
    PASSWORD='admin',
    ROOTFOLDER='/usr/share'
    #ROOTFOLDER='/home/acorrado/mediboard_project/ftp'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def import_datas():
  f = open('./exemple.yml')
  d_folders = yaml.load(f)
  f.close()
  if not d_folders:
      d_folders = {}
  return d_folders

def write_datas(d_folders):
  with open('exemple.yml', 'w') as outfile:
        outfile.write( yaml.dump(d_folders, default_flow_style=False) )
  for site in d_folders.keys():
    with open(site + '.csv' , 'w') as csvfile:
      fieldnames = ['Dossier','pwd','destinations','emails']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
      writer.writerow(dict((fn,fn) for fn in fieldnames))
      for dossier in d_folders[site].keys():
        writer.writerow({'Dossier':dossier, 'pwd':d_folders[site][dossier]['Password'], 'destinations':d_folders[site][dossier]['Hostnames'], 'emails':d_folders[site][dossier]['Receivers']})
      csvfile.close()

def get_sites():
    i = 0
    l_sites = {}
    #l_sites[i] = '/'
    d_folders = import_datas()
    #print(sorted(d_folders.iterkeys()))
    for site in sorted(d_folders.iterkeys()):
        #print(site)
    	#l_sites.append(site)
        i += 1
        l_sites[i] = site
    #print(type(l_sites))
    print(l_sites)
    return l_sites
  
def get_list():
     d = app.config['ROOTFOLDER']
     return [os.path.join(o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
#    return sorted(os.listdir(app.config['ROOTFOLDER']))
    
#@app.route('/', defaults={'path': '/'})
#@app.route('/<path>')
#@app.route('/')
@app.route('/sh')
def show_entries(path):
    error = None
    d_folders = import_datas()
    l_sites = get_sites()
    if not path in l_sites.values():
      abort(404)
    l_folders = get_list()
    #print(l_sites)
    return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, path=path, error=error)

@app.route('/exports/<path>/add', methods=['POST'])
def add_entry(path):
    error = None
    if not session.get('logged_in'):
        abort(401)
    d_folders = import_datas()
    test = [ x for x in d_folders[path] if x == str(request.form['Folder'])]
    l_dst = str(request.form['Hostnames']).split(',')
    l_mail = str(request.form['Receivers']).split(',')
    #print(str(request.form['Hostnames']).split())
    #print(l_dst.split(','))
    #print(l_dst)
    if not test:
      if request.form['Password'] != request.form['PasswordConfirm']:
         flash(u'Les mots de passes de correspondent pas', 'error')
      else:
        d_folders[path][str(request.form['Folder'])]= { 
            'Password':str(request.form['Password']), 
            #'Hostnames':str(request.form['Hostnames']), 
            'Hostnames': l_dst, 
            'Description':str(request.form['Description']), 
            #'Receivers':str(request.form['Receivers'])
            'Receivers': l_mail
        }
        write_datas(d_folders)
        flash('New entry was successfully posted')
    else:
      flash(u'Folder already exist for this site', 'error')
    return redirect(url_for('show_exports', path=path))
    #l_folders = sorted(os.listdir('/usr'))
    #return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=sorted(l_sites), error=error)
    #return redirect(url_for('show_entries', path=path))

@app.route('/exports/<path>/del', methods=['POST'])
def del_entry(path):
    if not session.get('logged_in'):
        abort(401)
    d_folders = import_datas()
    #print(type(request.form['Folder']))
    if request.form['Folder'] in d_folders[path]:
    #if True:
      #print('Site: %s, Dossier: %s' % (path,request.form['Folder']))
      del d_folders[path][request.form['Folder']] 
      write_datas(d_folders)
      flash('Entry was successfully delete')
    else:
      flash('This folder not exist in list')
    return redirect(url_for('show_exports', path=path))

#@app.route('/exports/<path>/validate')
#def validation(path):
#    if not session.get('logged_in'):
#        abort(401)
#    Site = path
    #print(Site)
    #d_folders = import_datas()
    #print(type(request.form['Folder']))
    #if request.form['Folder'] in d_folders[path]:
    #  del d_folders[path][request.form['Folder']] 
    #  write_datas(d_folders)
    #  flash('Entry was successfully delete')
    #else:
    #  flash('This folder not exist in list')
    #return redirect(url_for('show_exports', path=path))
#    return render_template('validation.html', Site=Site)

############## Sites
#@app.route('/select')
#def select_site():
#    #l_folders = os.listdir('/usr')
#    l_sites = [ 'SiteA' , 'SiteB', 'SiteC' ]
#    d_folders = import_datas()
#    return render_template('select_site.html', d_folders=d_folders, l_sites=l_sites)

#@app.route('/', defaults={'path': '/'})
############### 
#@app.route('/<path>')
#def show_conf(path):
#    #l_folders = os.listdir('/usr')
#    #l_sites = [ 'SiteA' , 'SiteB', 'SiteC' ]
#    d_folders = import_datas()
#    return render_template('show_yml.html', d_folders=d_folders )

@app.route('/add_site', methods=['POST'])
def add_site():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
      error = None
      #l_folders = sorted(os.listdir('/usr'))
      d_folders = import_datas()
      #l_sites = get_sites()
      test = [x for x in d_folders.keys() if x == str(request.form['Site'])]
      if not test:
        if (' ' in str(request.form['Site'])) == True:
          flash(u'No space please', 'error')
        else:
          Site = str(request.form['Site'])
          #Description = str(request.form['Description'])
          d_folders[str(Site)] = {}
          #d_folders[str(Site)]['Description'] = Description
          #print(d_folders)
          write_datas(d_folders)
          flash('New site was successfully added')
          #return redirect(url_for('show_entries'))
      else:
        flash(u'This Site already exist in list', 'error')
    return redirect(url_for('show_sites'))

@app.route('/del_site', methods=['POST'])
def del_site():
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
      d_folders = import_datas()
      if request.form['Site'] in d_folders.keys():
        del d_folders[request.form['Site']] 
        write_datas(d_folders)
        flash('Site was successfully delete')
     #   return redirect(url_for('show_entries'))
      else:
        flash(u'This Site not exist in list', 'error')
    return redirect(url_for('show_sites'))
    #return render_template('show_entries.html', error=error)
    #return redirect(url_for('show_entries'))

############## Upload
@app.route('/<path>/yml')
def show_yml(path):
    if not session.get('logged_in'):
        abort(401)
    d_folders = import_datas()
    return render_template('show_yml.html', d_folders=d_folders, path=path)

############## Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #print('User: %s login with password: %s' % (request.form['username'], request.form['password'])) 
      if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
        error = 'Invalid Credentials'
      else:
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('show_home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    #flash('You were logged out')
    return redirect(url_for('login'))
    #return redirect(url_for('show_entries'))

##################    With Zurb     #############

@app.route('/sites')
def show_sites():
    error = None
    if not session.get('logged_in'):
      #print('no logged user')
      #return render_template('login.html', error=error)
      return redirect(url_for('login'))
    d_folders = import_datas()
    l_sites = get_sites()
    l_folders = get_list()
    return render_template('show_sites.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, error=error)

@app.route('/admin')
def set_sites():
    error = None
    if not session.get('logged_in'):
      #print('no logged user')
      #return render_template('login.html', error=error)
      return redirect(url_for('login'))
    d_folders = import_datas()
    l_sites = get_sites()
    l_folders = get_list()
    flash(u'Je vous préviens encore parceque je suis simpa, Attention!', 'error')
    return render_template('set_sites.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, error=error)

#@app.route('/', defaults={'path': '/'})
#@app.route('/exports', defaults={'path': get_sites()[1] })
#@app.route('/<path>')
@app.route('/exports/<path>')
def show_exports(path):
#def show_exports():
    error = None
    if not session.get('logged_in'):
      return render_template('login.html', error=error)
    d_folders = import_datas()
    l_sites = get_sites()
    #if not path in l_sites.values():
    #  abort(404)
    l_folders = get_list()
    print(path)
    #print(l_sites)
    return render_template('show_exports.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, path=path, error=error)

@app.route('/new')
def show_new():
    error = None
    if not session.get('logged_in'):
      print('no logged user')
      return render_template('login.html', error=error)
    print('Logged user')
    d_folders = import_datas()
    l_sites = get_sites()
    #if not path in l_sites.values():
    #  abort(404)
    l_folders = get_list()
    #print(l_sites)
    #return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, path=path, error=error)
    return render_template('new.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, error=error)
    #return render_template('new.html')

#@app.route('/', defaults={'path': '/'})
@app.route('/')
@app.route('/home')
def show_home():
    error = None
    if not session.get('logged_in'):
      return render_template('login.html', error=error)
    return render_template('home.html', error=error )

@app.route('/newlayout')
def show_newlayout():
    error = None
    if not session.get('logged_in'):
      print('no logged user')
      return render_template('login.html', error=error)
    #print('Logged user')
    d_folders = import_datas()
    l_sites = get_sites()
    #if not path in l_sites.values():
    #  abort(404)
    l_folders = get_list()
    #print(l_sites)
    #return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, path=path, error=error)
    return render_template('newlayout.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, error=error)
    #return render_template('new.html')

#################################################

app.debug = True

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001)
