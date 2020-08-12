from neomodel import *

NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='driveyourplowoverthebonesofthedead'
NEO4J_SERVER='localhost'
NEO4J_PORT=7687

config.DATABASE_URL = f'bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@{NEO4J_SERVER}:{NEO4J_PORT}'  # default
config.ENCRYPTED_CONNECTION = False

# exit()
# G = Graph(password='drive your plow over the bones of the dead')
# Nodes = NodeMatcher(G)
# Edges = RelationshipMatcher(G)

class Media(StructuredNode):
    uid=UniqueIdProperty()
    ext=StringProperty()

    @property
    def filename(self):
        return self.uid[:3]+'/'+self.uid[3:]+self.ext


    @property
    def data(self):
        return {'uid':self.uid, 'ext':self.ext, 'filename':self.filename}


class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    name_irl = StringProperty()
    passkey = StringProperty()
    
    wrote = RelationshipTo('Post','WROTE')
    follows = RelationshipTo('Person','FOLLOWS')
    followed_by = RelationshipFrom('Person','FOLLOWS')
    located_in = RelationshipTo('Place','LOCATED_IN')
    in_group = RelationshipTo('Group','IN_GROUP')
    based_in = RelationshipTo('Place','LOCATED')
    has_avatar = RelationshipTo('Media','HAS_MEDIA')

    @property
    def img_src_avatar(self):
        avatar = self.has_avatar.first()
        if avatar:
            return avatar.filename
        return ''

    @property
    def data(self):
        img_avatar
        dx={'uid':self.uid, 'name':self.name, 'name_irl':self.name_irl,
            'img_src_avatar':self.img_src_avatar}


class Post(StructuredNode):
    # properties
    uid = UniqueIdProperty()
    content = StringProperty()
    timestamp = FloatProperty(index=True)

    # relations
    has_media = RelationshipTo('Media','HAS_MEDIA')
    written_by = RelationshipFrom('Person','WROTE')
    located_in = RelationshipTo('Place','LOCATED')

    @property
    def author(self):
        written_by = self.written_by
        if not written_by: return None
        person=written_by[0]
        person.passkey=None
        return person

    @property
    def img_src(self):
        # print(dir(self.has_media))
        if self.has_media:
            media = self.has_media[0]
            return media.filename
        return None

    @property
    def data(self):
        return {'uid':self.uid, 'content':self.content, 'img_src':self.img_src, 'timestamp':self.timestamp, 'author':self.author.name}


class Place(StructuredNode):
    # properties
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

    posted_in = RelationshipFrom('Post','LOCATED')
    based_in = RelationshipFrom('Person','LOCATED') 

    @property
    def data(self):
        return {'uid':self.uid, 'name':self.name}
    
    
class Group(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    motto = StringProperty()
    mission = StringProperty()

    has_members = RelationshipFrom('Person','IN_GROUP')

    @property
    def data(self):
        return {'uid':self.uid, 'name':self.name, 'motto':self.motto, 'mission':self.mission}



def test_models():
    jim = Person(name='Jim').save()
    post = Post(content='woooo').save()
    jim.wrote.connect(post)

    print(dir(post))
    print(jim.uid, post.uid)
    print(list(post.written_by.all()))

    print(post.author)


if __name__ == '__main__':
    test_models()