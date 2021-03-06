import web
import mistune
from datetime import datetime
import base64
import re
import hashlib
import sqlite3

render = web.template.render('templates/',globals={'datetime':datetime, 'len':len},base='base')
urls = (
    '/', 'index',
    '/login','login',
    '/note', 'note',
    '/folders', 'folders',
    '/folder_notes', 'folder_notes',
    '/tags', 'tags',
    '/tag_notes', 'tag_notes',
    '/:/(.*)', 'resources'
)

class index:

    text_search_form = web.form.Form(
        web.form.Textbox('search', web.form.notnull,
        description="Text Search:"),
        web.form.Button('Search'),
    )

    def GET(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        i = web.input(sort="myfolder_titles.breadcrumb_title",sort_order="ASC", page=1)
        page = int(i.page)
        perpage = 50
        offset = (page - 1) * perpage
        sort = " Order By %s %s" % (i.sort,i.sort_order)
        limit = " LIMIT %s, %s" % (offset, perpage)
        sql = "Select myfolder_titles.breadcrumb_title AS folders_title, myfolder_titles.id AS folders_id, notes.title As notes_title, notes.id as notes_id, notes.updated_time as notes_updated_time, length(notes.body) as notes_size, substr(notes.body,1,40) as notes_sample From notes Inner Join myfolder_titles On myfolder_titles.id = notes.parent_id" + sort + limit
        db = web.database(dbn='sqlite', db='database.sqlite')
        rows = db.query(sql)
        rowcount = db.query("SELECT COUNT(*) AS count FROM notes")[0]
        pages = int(rowcount.count / perpage)
        if rowcount.count % perpage > 0:
            pages += 1
        form = self.text_search_form()
        if page > pages:
            raise web.seeother('/')
        else:
            prev = page - 1
            if prev < 1:
                prev = 1
            next = page + 1
            if next > pages:
                next = pages
            return render.index(rows, form, page, prev, next, pages, i.sort, i.sort_order)

    def POST(self):
        form = self.text_search_form()
        if not form.validates():
            return render.search('Not Found', rows='')
        db = web.database(dbn='sqlite', db='database.sqlite')
        search_str = '%' + form.d.search + '%'
        rows = db.select('notes', where="title like $var or body like $var", vars={'var':search_str})
        return render.search('Text Search - '+form.d.search, rows)

class login:

    def GET(self):
        auth_str = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth_str is None:
            authreq = True
        else:
            auth_str = re.sub('^Basic ','',auth_str)
            auth_b = auth_str.encode()
            auth_decode = base64.decodebytes(auth_b)
            auth_str = auth_decode.decode()
            username,password = auth_str.split(':')
            configdb = sqlite3.connect('config.sqlite')
            passwdhash = hashlib.md5(password.encode()).hexdigest()
            cursor = configdb.execute('select * from passwd where uname=? and passwd=?', (username, passwdhash))
            row = cursor.fetchone()
            if row:
                raise web.seeother('/')
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate','Basic realm="Joplin Webview"')
            web.ctx.status = '401 Unauthorized'
            return

class note:
    text_search_form = web.form.Form(
        web.form.Textbox('search', web.form.notnull,
        description="Text Search:"),
        web.form.Button('Search'),
    )

    def GET(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        db = web.database(dbn='sqlite', db='database.sqlite')
        i = web.input(id=None)

        tags = db.query("Select tags.id, tags.title From notes Inner Join note_tags On note_tags.note_id = notes.id Inner Join tags On tags.id = note_tags.tag_id WHERE notes.id = $id", vars=dict(id=i.id))
        rows = db.select('notes', where={'id': i.id})
        for row in rows:
            return render.note(row.title, mistune.markdown(row.body), row, tags)

    def POST(self):
        form = self.text_search_form()
        if not form.validates():
            return render.search('Not Found', rows='')
        db = web.database(dbn='sqlite', db='database.sqlite')
        search_str = '%' + form.d.search + '%'
        rows = db.select('notes', where="title like $var or body like $var", vars={'var':search_str})
        return render.search('Text Search - '+form.d.search, rows)

class folders:
    text_search_form = web.form.Form(
        web.form.Textbox('search', web.form.notnull,
        description="Text Search:"),
        web.form.Button('Search'),
    )

    def GET(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        db = web.database(dbn='sqlite', db='database.sqlite')
        rows = db.query("Select myfolder_titles.id as folders_id, myfolder_titles.breadcrumb_title AS folders_title,  myfolder_titles.title AS folders_titleX, myfolder_titles.title_level AS folders_level, note_count_by_folder.rec_count AS folders_count From myfolder_titles left outer join note_count_by_folder On note_count_by_folder.parent_id = myfolder_titles.id Order By myfolder_titles.full_title")
        return render.folders(rows)

    def POST(self):
        form = self.text_search_form()
        if not form.validates():
            return render.search('Not Found', rows='')
        db = web.database(dbn='sqlite', db='database.sqlite')
        search_str = '%' + form.d.search + '%'
        rows = db.select('notes', where="title like $var or body like $var", vars={'var':search_str})
        return render.search('Text Search - '+form.d.search, rows)

class folder_notes:
    text_search_form = web.form.Form(
        web.form.Textbox('search', web.form.notnull,
        description="Text Search:"),
        web.form.Button('Search'),
    )

    def GET(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        i = web.input(id=None)
        db = web.database(dbn='sqlite', db='database.sqlite')
        folders = db.select('myfolder_titles', where={'id': i.id})
        folder_title = folders[0].breadcrumb_title
        rows = db.select('notes', where={'parent_id': i.id})
        return render.search('Folder Search - '+folder_title, rows)

    def POST(self):
        form = self.text_search_form()
        if not form.validates():
            return render.search('Not Found', rows='')
        db = web.database(dbn='sqlite', db='database.sqlite')
        search_str = '%' + form.d.search + '%'
        rows = db.select('notes', where="title like $var or body like $var", vars={'var':search_str})
        return render.search('Text Search - '+form.d.search, rows)

class tags:
    text_search_form = web.form.Form(
        web.form.Textbox('search', web.form.notnull,
        description="Text Search:"),
        web.form.Button('Search'),
    )

    def GET(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        db = web.database(dbn='sqlite', db='database.sqlite')
        rows = db.select('note_count_by_tag',order='tag_title')
        return render.tags(rows)

    def POST(self):
        form = self.text_search_form()
        if not form.validates():
            return render.search('Not Found', rows='')
        db = web.database(dbn='sqlite', db='database.sqlite')
        search_str = '%' + form.d.search + '%'
        rows = db.select('notes', where="title like $var or body like $var", vars={'var':search_str})
        return render.search('Text Search - '+form.d.search, rows)

class tag_notes:
    text_search_form = web.form.Form(
        web.form.Textbox('search', web.form.notnull,
        description="Text Search:"),
        web.form.Button('Search'),
    )

    def GET(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        i = web.input(id=None)
        db = web.database(dbn='sqlite', db='database.sqlite')
        tags = db.select('tags', where={'id': i.id})
        tag_title = tags[0].title
        rows = db.query("Select notes.* From note_tags Inner Join notes On notes.id = note_tags.note_id WHERE tag_id = $tag_id", vars=dict(tag_id=i.id))
#        rows = db.query("Select tags.title As tags_title, notes.* From note_tags Inner Join notes On notes.id = note_tags.note_id Inner Join tags On tags.id = note_tags.tag_id WHERE tag_id = $tag_id", vars=dict(tag_id=i.id))
        return render.search('Tag Search - ' + tag_title, rows)

    def POST(self):
        form = self.text_search_form()
        if not form.validates():
            return render.search('Not Found', rows='')
        db = web.database(dbn='sqlite', db='database.sqlite')
        search_str = '%' + form.d.search + '%'
        rows = db.select('notes', where="title like $var or body like $var", vars={'var':search_str})
        return render.search('Text Search - '+form.d.search, rows)

import os
import glob
class resources:
    def GET(self,resource):
        name = glob.glob('resources/%s*' %  resource)
        ext = name[0].split(".")[-1] # Gather extension

        cType = {
            "doc":"application/msword",
            "docx":"application/msword",
            "pdf":"application/pdf",
            "zip":"application/zip",
            "xls":"application/vnd.ms-excel",
            "xlsx":"application/vnd.ms-excel",
            "pptx":"application/vnd.ms-powerpoint",
            "png":"image/png",
            "svg":"image/svg",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon",
            "csv":"text/csv",
            "txt":"text/plain"
            }

        if name: 
            web.header("Content-Type", cType[ext]) # Set the Header
            return open(name[0],"rb").read() # Notice 'rb' for reading resources
        else:
            raise web.notfound()

from cheroot.server import HTTPServer
from cheroot.ssl.builtin import BuiltinSSLAdapter

HTTPServer.ssl_adapter = BuiltinSSLAdapter(
        certificate='./server.cert',
        private_key='./server.key')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
