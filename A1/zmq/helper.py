from enum import Enum

class REQUEST(Enum):
    '''
    class to enumerate all the request types
    '''
    Register = 1
    GetServerList = 2
    JoinServer = 3
    LeaveServer = 4
    GetArticles = 5
    PublishArticle = 6
    

class Node:
    '''
    class for server and client nodes
    '''
    def __init__(self, name, addr):
        '''
        initialize the node
        '''
        self.name = name
        self.addr = addr 

    def __str__(self):
        '''
        prints the node info
        '''
        return str(self.name) + " - " + str(self.addr)
    

class Article:
    validTypes = ["SPORTS", "FASHION", "POLITICS"]
    def __init__(self, type, author, time, content):
        if type not in self.validTypes or len(time) != 0 or len(content) > 200:
            raise ValueError("Illegal Article")
        
        self.type = type
        self.author = author
        self.time = time
        self.content = content

    def __str__(self):
        '''
        prints the node info
        '''
        return str(self.type) \
            + "\n" + str(self.author) \
            + "\n" + str(self.time) \
            + "\n" + str(self.content)
 
            
class ArticleRequest:
    def __init__(self, type, author, time):
        self.type = type
        self.author = author
        self.time = time
    
    def __str__(self):
        '''
        prints the node info
        '''
        return str(self.type) + ", " + str(self.author) + ", " + str(self.time)
            
    def satisfy(self, article):
        '''
        checks if the article satisfy the article request
        '''
        
        if len(self.type) != 0 and self.type != article.type:
            return 0
        if len(self.author) != 0 and self.author != article.author:
             return 0
        if len(self.time) != 0 and self.time > article.time:
             return 0
        return 1 