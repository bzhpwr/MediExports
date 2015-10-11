import os, yaml, uuid
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
#from Crypto.Hash import SHA256
#from Crypto.Cipher import AES

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    SECRET_CBC='',
    USERNAME='admin',
    #PASSWORD='\x8civ\xe5\xb5A\x04\x15\xbd\xe9\x08\xbdM\xee\x15\xdf\xb1g\xa9\xc8s\xfcK\xb8\xa8\x1fo*\xb4H\xa9\x18'
    PASSWORD='admin',
    ROOTFOLDER='/usr'
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
  
def get_sites():
    i = 0
    l_sites = {}
    l_sites[i] = '/'
    d_folders = import_datas()
    #print(sorted(d_folders.iterkeys()))
    for site in sorted(d_folders.iterkeys()):
        #print(site)
    	#l_sites.append(site)
        i += 1
        l_sites[i] = site
    #print(type(l_sites))
    #print(l_sites)
    return l_sites
  
def get_list():
    return sorted(os.listdir(app.config['ROOTFOLDER']))
    
@app.route('/', defaults={'path': '/'})
@app.route('/<path>')
#@app.route('/')
def show_entries(path):
    error = None
    d_folders = import_datas()
    l_sites = get_sites()
    if not path in l_sites.values():
      abort(404)
    l_folders = get_list()
    #print(l_sites)
    return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=l_sites, path=path, error=error)

@app.route('/<path>/add', methods=['POST'])
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
            #'Receivers':str(request.form['Receivers'])
            'Receivers': l_mail
        }
        write_datas(d_folders)
        flash('New entry was successfully posted')
    else:
      flash(u'Folder already exist for this site', 'error')
    return redirect(url_for('show_entries', path=path))
    #l_folders = sorted(os.listdir('/usr'))
    #return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=sorted(l_sites), error=error)
    #return redirect(url_for('show_entries', path=path))

@app.route('/<path>/del', methods=['POST'])
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
    return redirect(url_for('show_entries', path=path))

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
          d_folders[str(Site)] = {}
          write_datas(d_folders)
          flash('New site was successfully added')
          #return redirect(url_for('show_entries'))
      else:
        flash(u'This Site already exist in list', 'error')
    return redirect(url_for('show_entries'))
    #return render_template('show_entries.html', d_folders=d_folders, l_folders=l_folders, l_sites=sorted(l_sites), error=error)
    #return render_template('show_entries.html', error=error)

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
    return redirect(url_for('show_entries'))
    #return render_template('show_entries.html', error=error)
    #return redirect(url_for('show_entries'))

############## Upload
@app.route('/<path>/yml')
def show_yml(path):
    if not session.get('logged_in'):
        abort(401)
    #l_folders = os.listdir('/usr')
    #l_sites = [ 'SiteA' , 'SiteB', 'SiteC' ]
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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

app.debug = True

if __name__ == '__main__':
  app.run(host='0.0.0.0')
