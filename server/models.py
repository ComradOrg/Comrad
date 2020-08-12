
from py2neo import *
from py2neo.ogm import *

G = Graph(password='drive your plow over the bones of the dead')
Nodes = NodeMatcher(G)
Edges = RelationshipMatcher(G)



class MyGraphObject(GraphObject):
    @property
    def data(self):
        return dict(self.__ogm__.node)

class Person(MyGraphObject):
    __primarykey__ = 'name'

    name = Property()
    name_irl = Property()
    passkey = Property()

    posts = RelatedTo('Post','WROTE')
    follows = RelatedTo('Person','FOLLOWS')
    followers = RelatedFrom('Person','FOLLOWS')
    based_in = RelatedTo('Place','BASED_IN')
    groups = RelatedTo('Group','IN_GROUP')
    avatar = RelatedTo('Media','HAS_MEDIA')

class Post(MyGraphObject):
    # properties
    title = Property()
    content = Property()
    img_src = Property()

    # relations
    author = RelatedFrom('Person','WROTE')
    location = RelatedTo('Place','BASED_IN')


    @property
    def data(self):
        dx=dict(self.__ogm__.node)

        authors=list(self.author)
        locations=list(self.location)
        dx['author']=authors[0].name if authors else ''
        dx['location']=locations[0].name if locations else ''

        return dx

class Place(MyGraphObject):
    # properties
    __primarykey__ = 'name'
    name = Property()
    
    # relations
    citizens = RelatedFrom('Person','BASED_IN')

class Group(MyGraphObject):
    # properties
    __primarykey__ = 'name'
    name = Property()
    motto = Property()
    mission = Property()

    # relations
    members = RelatedFrom('Person','IN_GROUP')



def test_models():
    x = Person(); x.name='MrX'
    y = Person(); y.name='MrY'
    p1 = Post(); p1.title='Post 1'; p1.content='Hello world!'
    p2 = Post(); p2.title='Post 2'; p2.content='Hello world!!!'
    p3 = Post(); p3.title='Post 3'; p3.content='Hello world!!!!!!!!!!!!'

    x.follows.add(y)
    x.posts.add(p1)
    y.posts.add(p2)
    G.push(y)

    y.posts.add(p3)

    g1=Group(); g1.name='BlocBloc'
    c1=Place(); c1.name='Utopia'
    c2=Place(); c2.name='Dystopia'

    x.based_in.add(c1)
    y.based_in.add(c2)

    x.groups.add(g1)
    y.groups.add(g1)    



    for a in [x,y,p1,p2,p3,g1,c1,c2]: G.push(a)
    


# test_models()


