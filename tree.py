class Tree(object):
    def __init__(self, node=None, children=None, login="", password=""):
        self.name=node['name'].strip()
        self.label=node['label'].strip()
        self.type=node['type']
        self.login=login
        self.password=password
        self.children=[]
        if children is not None:
            for child in children:
                self.add_child(child)
    
    def __repr__(self):
        return '(' +  self.login + ' ; ' + self.password + ' ; ' + self.name + ' ; ' + self.label + ' ; ' + self.type + ' ; ' + str(len(self.children)) + ')'
    
    def add_child(self, node):
        self.children.append(node)

