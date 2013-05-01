

def get_tasks():

    tasks = []
    task_ptn = re.compile('(?:an?|the) ([\w\-]+) task', re.I)

    for art in session.query(Article):
        print 'Working on article %s...' % (art.pmid)
        html = loadhtml(art)
        if html:
            search = task_ptn.search(html)
            if search:
                print search.groups()[0]
                tasks.append(search.groups()[0])

    return tasks
