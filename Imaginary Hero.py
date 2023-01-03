import pygame
from time import sleep
from pygame.image import load
import random
import csv
import copy

##init
pygame.init()
width = 800
height = 500
FPS = 60
FONT = pygame.font.SysFont("comicsansms", 18)
CLOCK = pygame.time.Clock()
Screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Imaginary Hero")
pygame.display.set_icon(load("assets/ICON.png"))
map = None
notice_board = None
condition = {}
mouse_pos = [0,0]
destory = False
assets = {}

##image loading
if True:
    assets["player"] = {"[0, -1]":[load("assets/player/player_up1.png"),load("assets/player/player_up2.png")],"[0, 1]":[load("assets/player/player_down1.png"),load("assets/player/player_down2.png")],"[-1, 0]":[load("assets/player/player_left1.png"),load("assets/player/player_left2.png")],"[1, 0]":[load("assets/player/player_right1.png"),load("assets/player/player_right2.png")],"jump":[load("assets/player/player_jump.png")],"swim":[load("assets/player/player_swim1.png"),load("assets/player/player_swim2.png")]}
    assets["notice"] = load("assets/notice.png")
    assets["wall_h"] = load("assets/wall_h.png")
    assets["wall_v"] = load("assets/wall_v.png")
    assets["city"] = load("assets/city.png")
    assets["shop"] = load("assets/shop.png")
    assets["menu"] = load("assets/menu.png")
    assets["logo"] = load("assets/logo.png")
    assets["save1"] = load("assets/save1.png")
    assets["save2"] = load("assets/save2.png")
    assets["button"] = load("assets/button.png")
    assets["loading"] = load("assets/refresh.png")
    assets["loading"].blit(FONT.render("Loading...",True,[255,255,255]),[340,220])
    assets["credit"] = load("assets/credit.png")
    assets["score"] = load("assets/score.png")
    assets["guide"] = load("assets/guide.png")
    assets["tp"] = [load("assets/tp/1.png"),load("assets/tp/2.png"),load("assets/tp/3.png")]
    assets["child"] = load("assets/child.png")
    assets["ring"] = load("assets/ring.png")
    assets["teeth"] = load("assets/teeth.png")
    assets["blank"] = load("assets/blank.png")
    assets["fountain"] = load("assets/fountain.png")
    assets["grandpa"] = load("assets/grandpa.png")
    assets["grandma"] = load("assets/grandma.png")
    assets["dog"] = load("assets/dog.png")
    assets["robber"] = load("assets/robber.png")
    assets["bullet"] = load("assets/bullet.png")
    assets["heart"] = load("assets/heart.png")
    assets["search"] = []
    assets["building"] = []
    assets["tree"] = [load("assets/tree1.png"),load("assets/tree2.png")]
    assets["flower"] = [load("assets/flower1.png"),load("assets/flower2.png")]
    assets["river"] = [load("assets/river/river1.png"),load("assets/river/river2.png"),load("assets/river/river3.png"),load("assets/river/river4.png"),load("assets/river/river3.png"),load("assets/river/river2.png")]
    assets["tip"] = load("assets/tip.png")
    assets["life"] = load("assets/life.png")
    assets["underwater"] = [load("assets/underwater/underwater1.png"),load("assets/underwater/underwater2.png"),load("assets/underwater/underwater3.png")]
    assets["tips"] = ["jump over short walls?","Q improves ur eyesight?","maybe there are treasures in the river","dogs are pretty scary, but they are cute","our river is pretty deep huh?","our citizens tend to lose their stuff...","no, ur mouse is not useless","coffee is bad for you","given enough care plants can grow","shift key is quite useful","sike","sike","sike","humans run pretty fast!","press x to doubt","press f to pay respect","we encourage spamming","dieing is gay, but it can be avoided"]
    for i in range(1,9):
        ii = str(i)
        assets["building"].append(load("assets/building/building"+ii+".png"))
    for i in range(1,16):
        ii = str(i)
        assets["search"].append(load("assets/search/"+ii+".png"))
    pygame.mixer.music.load("music/Imaginary.mp3")

##classes
class Animation:
    def __init__(self,name,img,slow,loop = False):
        self.name = name
        self.img = img
        self.slow = slow
        self.loop = loop
        self.idx1 = 0
        self.idx2 = 0
        self.maxi = len(img)-1
    def get_name(self):
        return self.name
    def tick(self):
        self.idx1 += 1
        if self.idx1 == self.slow:
            self.idx1 = 0
            self.idx2 += 1
            if self.idx2 > self.maxi:
                if self.loop:
                    self.idx2 = 0
                    return False
                else:
                    return True
    def dis(self):
        return self.img[self.idx2]
class Object:
    def __init__(self,name,sprite,slow,loop,pos,hitbox,hit_level):
        self.name = name
        self.sprite = Animation(name,sprite,slow,loop)
        self.pos = list(pos)
        self.hitbox = hitbox
        self.hit_level = hit_level
    def add_hitbox(self,size):
        self.hitbox.append(pygame.Rect(self.pos[0],self.pos[1],size[0],size[1]))
    def collide_pt(self,pts):
        for box in self.hitbox:
            for pt in pts:
                if box.collidepoint(pt):
                    return self.name
        return False
    def collide_rect(self,rects):
        for box in self.hitbox:
            for rect in rects:
                if box.colliderect(rect):
                    return self.name
        return False
    def tick(self):
        if self.sprite.tick():
            return True
    def dis(self):
        Screen.blit(self.sprite.dis(),self.pos)
class Notice:
    def __init__(self,stri):
        self.stri = stri
        self.n = assets["notice"].copy()
        self.n.blit(FONT.render(stri,True,(0,0,0)),(40,5))
        self.sprite = Animation("notice",[self.n],1,True)
        self.frame = 0
    def dis(self):
        Screen.blit(self.sprite.dis(),(200,height-self.frame/5))
    def tick(self):
        if self.frame < 300:
            self.frame += 2
        else:
            return True
class Player(Object):
    def __init__(self,name,sprite,slow,loop):
        super().__init__(name,sprite["[0, 1]"],slow,loop,[1,250],[pygame.Rect(0,0,30,40)],0)
        self.slow = slow
        self.loop = loop
        self.sprites = sprite
        self.stats = {"jump":0,"dir":str([0, 1]),"inv":[],"invi":False,"swim":False}
    def add_to_inv(self,a):
        self.stats["inv"].append(a)
    def up(self):
        if self.stats["jump"] == 0:
            self.stats["jump"] = 30
            return True
        else:
            return False
    def move(self,dir):
        if str(dir) != "[0, 0]" and test_double(dir) == False:
            self.stats["dir"] = str(dir)
            self.sprite = Animation("ani",self.sprites[self.stats["dir"]],self.slow,self.loop)
        self.pos[0] += dir[0]
        self.pos[1] += dir[1]
        self.hitbox[0].update(self.pos[0]+5,self.pos[1],30,40)
    def tick(self):
        safe = True
        if self.stats["invi"]:
            self.sprite = Animation("invi",[assets["blank"]],self.slow,True)
            self.stats["invi"] = False
            safe = False
        elif self.stats["jump"] != 0:
            self.sprite = Animation("jump",self.sprites["jump"],self.slow,True)
            self.stats["jump"] -= 1
            safe = False
        elif self.stats["swim"]:
            if self.sprite.name != "swim":
                self.sprite = Animation("swim",self.sprites["swim"],self.slow,True)
            self.stats["swim"] = False
            safe = False
        if self.sprite.name != "ani" and safe:
                self.sprite = Animation("ani",self.sprites[self.stats["dir"]],self.slow,self.loop)
        super().tick()
class Wall(Object):
    def __init__(self,pos,dir):
        if dir == "v":
            super().__init__("wall",[],1,True,pos,[pygame.Rect(pos[0],pos[1],40,210)],3)
            self.sprite = Animation("wall",[assets["wall_v"]],1,True)
        elif dir == "h":
            super().__init__("wall",[],1,True,pos,[pygame.Rect(pos[0],pos[1],320,40)],3)
            self.sprite = Animation("wall",[assets["wall_h"]],1,True)
class Building(Object):
    def __init__(self,loc):
        size = [280,170]
        pos = [40,40]
        if loc == 1:
            pos = [40,40]
        elif loc == 2:
            pos = [480,40]
        elif loc == 3:
            pos = [40,290]
        elif loc == 4:
            pos = [480,290]
        super().__init__("building",[random.choice(assets["building"])],1,True,pos,[pygame.Rect(pos[0],pos[1],size[0],size[1])],2)
class Shop(Object):
    def __init__(self,loc):
        size = [280,170]
        pos = [40,40]
        if loc == 1:
            pos = [40,40]
        elif loc == 2:
            pos = [480,40]
        elif loc == 3:
            pos = [40,290]
        elif loc == 4:
            pos = [480,290]
        super().__init__("shop",[assets["shop"]],1,True,pos,[pygame.Rect(pos[0],pos[1],size[0],size[1])],2)
class Border(Object):
    def __init__(self,size,pos):
        super().__init__("border",[assets["blank"]],1,True,pos,[pygame.Rect(pos[0],pos[1],size[0],size[1])],3)
class Button(Object):
    def __init__(self,pos,stri,func):
        self.func = func
        tem = assets["button"].copy()
        tem.blit(FONT.render(stri,True,[0,0,0]),[15,8])
        super().__init__("button",[tem],1,True,pos,[pygame.Rect(pos[0],pos[1],100,40)],4)
    def tick(self,p):
        if self.collide_pt([p]):
            return self.func
class Item(Object):
    def __init__(self,name,sprite,pos):
        self.blank = assets["blank"]
        self.og = sprite
        self.ogh = pygame.Rect(pos[0],pos[1],32,32)
        super().__init__("item_"+name,[self.blank],1,True,pos,[],2)
    def hide(self):
        self.sprite = Animation("a",[self.blank],1,True)
        self.hitbox = []
    def show(self):
        self.sprite = Animation("a",self.og,1,True)
        self.hitbox = [self.ogh]
class Fountain(Object):
    def __init__(self,pos):
        super().__init__("fountain",[assets["fountain"]],1,True,pos,[pygame.Rect(pos[0],pos[1],100,4),pygame.Rect(pos[0],pos[1],4,100),pygame.Rect(pos[0]+96,pos[1],4,100),pygame.Rect(pos[0],pos[1]+96,100,4)],1)
class River(Object):
    def __init__(self):
        super().__init__("river",assets["river"],30,True,[479,0],[pygame.Rect(479,0,10,500)],1)
class Water(Object):
    def __init__(self,pos,size,river = False):
        super().__init__("water",[assets["blank"]],1,True,pos,[pygame.Rect(pos[0],pos[1],size[0],size[1])],5)
        if river:
            self.name = "river"
class NPC(Object):
    def __init__(self,name,sprite,pos,need):
        self.need = need
        super().__init__("NPC_"+name,sprite,1,True,pos,[pygame.Rect(pos[0]+7,pos[1],25,40)],2)
class Tip(Object):
    def __init__(self,pos):
        super().__init__("tip",[assets["tip"]],1,True,pos,[pygame.Rect(pos[0],pos[1],10,20)],3)
        self.content = random.choice(assets["tips"])
class Enemy(Object):
    def __init__(self,name,sprite,pos):
        self.kill = True
        self.savable = True
        super().__init__("enemy_"+name,sprite,1,True,pos,[pygame.Rect(pos[0]+5,pos[1]+5,30,30)],2)
class Bullet(Object):
    def __init__(self,pos):
        self.kill = True
        self.savable = False
        super().__init__("enemy_bullet",[assets["bullet"]],300,False,pos,[pygame.Rect(pos[0],pos[1],4,4)],6)
    def tick(self):
        self.pos[0] -= 1
        self.hitbox = [pygame.Rect(self.pos[0],self.pos[1],4,4)]
        return super().tick()
class Robber(Enemy):
    def __init__(self,pos):
        super().__init__("enemy_robber",[assets["robber"]],pos)
        self.hitbox = [pygame.Rect(self.pos[0],self.pos[1],40,40)]
    def tick(self):
        super().tick()
        if random.choice(range(120)) == 69:
            map.add_obj([Bullet([self.pos[0],self.pos[1]+6])])
class Plant(Object):
    def __init__(self,name,sprite,pos):
        self.sprites = sprite
        self.age = 0
        super().__init__("plant_"+name,[self.sprites[0]],1,True,pos,[pygame.Rect(pos[0],pos[1],40,40)],2)
    def grow(self):
        self.sprite = Animation("plant",[self.sprites[1]],1,True)
    def tick(self):
        if self.age == 300:
            self.grow()
        super().tick()
class Life(Object):
    def __init__(self,pos):
        super().__init__("life",[assets["life"]],1,True,pos,[pygame.Rect(pos[0],pos[1],32,32)],3)
class Objects:
    def __init__(self):
        self.objects = []
    def add_obj(self,new):
        self.objects += new
    def get_hitbox(self,level):
        res = []
        for obj in self.objects:
            try:
                if obj.hit_level <= level:
                    res += obj.hitbox
            except:
                continue
        return res
    def get_shopbox(self):
        res = []
        for obj in self.objects:
            try:
                if obj.name == "shop":
                    res += obj.hitbox
            except:
                continue
        return res
    def kick(self,i):
        self.objects.remove(i)
    def collide_pt(self,pts,level):
        for obj in self.objects:
            if obj.hit_level in level:
                if obj.collide_pt(pts) != False:
                    return obj
    def collide_rect(self,rects,level):
        for obj in self.objects:
            if obj.hit_level in level:
                if obj.collide_rect(rects) != False:
                    return obj
    def unhide(self):
        self.add_obj([Object("search",assets["search"],1,False,[0,0],[],4)])
        for obj in self.objects:
            if "item" in obj.name:
                obj.show()
    def tick(self):
        for obj in self.objects:
            if obj.tick():
                self.objects.remove(obj)
    def dis(self):
        for obj in self.objects:
            obj.dis()
class Score_board:
    def __init__(self,content):
        self.content = content
        self.scroll_ind = 0
        self.base = assets["score"]
        self.sprite = self.base.copy()
    def scroll(self,y):
        max = len(self.content)-1
        min = 0
        new = self.scroll_ind - y
        if new >= min and new <= max:
            self.scroll_ind = new
    def get_score(self):
        self.sprite = self.base.copy()
        content = self.content[self.scroll_ind:self.scroll_ind+9]
        for ind in range(len(content)):
            n = assets["notice"].copy()
            n.blit(FONT.render(content[ind],True,(0,0,0)),(40,5))
            self.sprite.blit(n,[0,40*ind])
        return self.sprite.copy()
def location_check(pl):
    if pl.pos[0] == -5:
        pl.pos[0] = 759
        return pl.pos
    if pl.pos[0] == 765:
        pl.pos[0] = 1
        return pl.pos
    if pl.pos[1] == 0:
        pl.pos[1] = 459
        return pl.pos
    if pl.pos[1] == 460:
        pl.pos[1] = 1
        return pl.pos
def add_notice(stri,grp):
    grp.add_obj([Notice(stri)])
def refresh(m,ply,n):
    m.tick()
    ply.tick()
    m.dis()
    ply.dis()
    try:
        if n.objects[0].tick():
            n.kick(n.objects[0])
        n.objects[0].dis()
    except:
        pass
    pygame.display.update()
def load_screen():
    Screen.blit(assets["loading"],[0,0])
    pygame.display.update()
    sleep(1)
def get_list():
    with open("data/game_data.csv","r") as data:
        data = csv.reader(data,delimiter = ",")
        tem = 1
        for i in data:
            if tem == 1:
                tem = i
    return tem
def test_double(lst):
    if lst[0] != 0 and lst[1] != 0:
        return True
    else:
        return False
def rand_pos(building,size,ban = None):
    ranges = [[40,320,40,210],[320,480,0,210],[480,760,40,210],[0,320,210,290],[320,480,210,290],[480,800,210,290],[40,320,290,460],[320,480,290,500],[480,760,290,460]]
    if building:
        blocks = range(1,10)
    else:
        blocks = [2,4,5,6,8]
    if ban != None:
        blocks.remove(ban)
    block_selection = random.choice(blocks)
    return [random.choice(range(ranges[block_selection-1][0],ranges[block_selection-1][1]-size[0])),random.choice(range(ranges[block_selection-1][2],ranges[block_selection-1][3]-size[1]))]
def map_gen(underwater,x):
    final_map = []
    final_map += [Border([width,2],[0,-2]),Border([2,height],[width,0]),Border([width,2],[0,height]),Border([2,height],[-2,0])]
    slot = {"1":[40,40],"2":[480,40],"3":[40,290],"4":[480,290]}
    if underwater:
        final_map += [Border([320,2],[0,0]),Border([320,2],[480,0]),Border([2,500],[0,0]),Border([2,500],[798,0]),Border([800,2],[0,498])]
        final_map += [Object("underwater",assets["underwater"],30,True,[0,0],[],4),Water([0,0],[800,500],False)]
        final_map += [Life([400-16,250-16])]
        return final_map
    else:
        if random.choice(range(1,25)) == 1 and x[0] < 600:
            final_map += [Object("city",[assets["city"]],1,True,[0,0],[],4)]
            final_map += [Wall([0,0],"h"),Wall([0,0],"v"),Wall([480,0],"h"),Wall([760,0],"v"),Wall([0,460],"h"),Wall([0,290],"v"),Wall([480,460],"h"),Wall([760,290],"v"),Wall([760,210],"v")]
            final_map += [Building(1),Building(3)]
            final_map += [River(),Water([489,0],[310,500],True)]
        else:
            if random.choice(range(1,10)) == 1:
                final_map += [Object("city",[assets["city"]],1,True,[0,0],[],4)]
                final_map += [Wall([0,0],"h"),Wall([0,0],"v"),Wall([480,0],"h"),Wall([760,0],"v"),Wall([0,460],"h"),Wall([0,290],"v"),Wall([480,460],"h"),Wall([760,290],"v")]
                blank = random.choice([1,2,3,4])
                #spawn tip
                for i in range(random.choice([0,0,0,0,0,0,0,1,1,1,1,2,2,3])):
                    final_map += [Tip(rand_pos(True,[10,20]))]
                #spawn item
                if random.choice(range(1,10)) == 1:
                    final_map += [random.choice([Item("child",[assets["child"]],rand_pos(True,[32,32])),Item("teeth",[assets["teeth"]],rand_pos(True,[32,32])),Item("ring",[assets["ring"]],rand_pos(True,[32,32]))])]
                #spawn building
                tem = [Building(1),Building(2),Building(3),Building(4)]
                tem.pop(blank-1)
                final_map += tem
                #spawn npc
                ban = None
                if x[0] < 100:
                    ban = 4
                if x[0] > 700:
                    ban = 6
                if x[1] < 100:
                    ban = 2
                if x[1] > 400:
                    ban = 8
                if random.choice(range(1,10)) == 1:
                    final_map += [random.choice([NPC("grandma",[assets["grandma"]],rand_pos(False,[40,40],ban),"item_"+random.choice(["child","ring","teeth"])),NPC("grandpa",[assets["grandpa"]],rand_pos(False,[40,40],ban),"item_"+random.choice(["child","ring","teeth"])),Enemy("dog",[assets["dog"]],rand_pos(False,[40,40],ban)),Robber(rand_pos(False,[40,40],ban))])]
                #extra building
                building = random.choice(["shop","fountain","plant"])
                if building == "shop":
                    final_map += [Shop(blank)]
                if building == "fountain":
                    final_map += [Fountain([slot[str(blank)][0]+80,slot[str(blank)][1]+40])]
                    final_map += [Water([slot[str(blank)][0]+81,slot[str(blank)][1]+41],[98,98])]
                if building == "plant":
                    c = random.choice([1,2])
                    if c == 1:
                        final_map += [Plant("flower",assets["flower"],[slot[str(blank)][0]+80,slot[str(blank)][1]+40]),Plant("flower",assets["flower"],[slot[str(blank)][0]+120,slot[str(blank)][1]+40]),Plant("flower",assets["flower"],[slot[str(blank)][0]+80,slot[str(blank)][1]+80]),Plant("flower",assets["flower"],[slot[str(blank)][0]+120,slot[str(blank)][1]+80])]
                    else:
                        final_map += [Plant("tree",assets["tree"],[slot[str(blank)][0]+80,slot[str(blank)][1]+40]),Plant("tree",assets["tree"],[slot[str(blank)][0]+120,slot[str(blank)][1]+40]),Plant("tree",assets["tree"],[slot[str(blank)][0]+80,slot[str(blank)][1]+80]),Plant("tree",assets["tree"],[slot[str(blank)][0]+120,slot[str(blank)][1]+80])]
            else:
                final_map += [Object("city",[assets["city"]],1,True,[0,0],[],4)]
                final_map += [Wall([0,0],"h"),Wall([0,0],"v"),Wall([480,0],"h"),Wall([760,0],"v"),Wall([0,460],"h"),Wall([0,290],"v"),Wall([480,460],"h"),Wall([760,290],"v")]
                #spawn tip
                for i in range(random.choice([0,0,0,0,0,0,0,1,1,2])):
                    final_map += [Tip(rand_pos(True,[10,20]))]
                #spawn item
                if random.choice(range(1,10)) == 1:
                    final_map += [random.choice([Item("child",[assets["child"]],rand_pos(True,[32,32])),Item("teeth",[assets["teeth"]],rand_pos(True,[32,32])),Item("ring",[assets["ring"]],rand_pos(True,[32,32]))])]
                #spawn building
                final_map += [Building(1),Building(2),Building(3),Building(4)]
                #spawn npc
                ban = None
                if x[0] < 100:
                    ban = 4
                if x[0] > 700:
                    ban = 6
                if x[1] < 100:
                    ban = 2
                if x[1] > 400:
                    ban = 8
                if random.choice(range(1,10)) == 1:
                    final_map += [random.choice([NPC("grandma",[assets["grandma"]],rand_pos(False,[40,40],ban),"item_"+random.choice(["child","ring","teeth"])),NPC("grandpa",[assets["grandpa"]],rand_pos(False,[40,40],ban),"item_"+random.choice(["child","ring","teeth"])),Enemy("dog",[assets["dog"]],rand_pos(False,[40,40],ban)),Robber(rand_pos(False,[40,40],ban))])]
    return final_map

#app loop
run = True
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)
map = Objects()
map.add_obj(map_gen(False,[2,250]))
notice_board = Objects()
score_board = Score_board(get_list())
credit_group = [Object("menu",[assets["menu"]],1,True,[0,0],[],4),Object("credit",[assets["credit"]],1,True,[100,50],[],4),Button([10,450],"Back","back")]
score_group = [Object("menu",[assets["menu"]],1,True,[0,0],[],4),Button([10,450],"Back","back")]
end_group = [Object("menu",[assets["menu"]],1,True,[0,0],[],4),Object("save",[assets["save1"]],1,True,[180,100],[],4),Object("save",[assets["save2"]],1,True,[265,200],[],4),Button([350,250],"Yes","yes"),Button([350,300],"No","no")]
guide_group = [Object("menu",[assets["menu"]],1,True,[0,0],[],4),Object("guide",[assets["guide"]],1,True,[100,50],[],4),Button([10,450],"Back","back")]
menu_group = [Object("menu",[assets["menu"]],1,True,[0,0],[],4),Object("logo",[assets["logo"]],1,True,[62,100],[],4),Button([350,250],"Start","start"),Button([350,300],"Score","score"),Button([350,350],"Credits","credit"),Button([350,400],"Guide","guide"),Button([350,450],"Quit","quit")]
while run:
    #menu event
    mouse_pos = pygame.mouse.get_pos()
    game = False
    credit = False
    score = False
    guide = False
    events = pygame.event.get()
    r = None
    for event in events:
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for obj in menu_group:
                    if obj.name == "button":
                        r = obj.tick(mouse_pos)
                        if r != None:
                            break
        if r == "start":
            game = True
            load_screen()
        if r == "credit":
            credit = True
        if r == "score":
            score = True
        if r == "guide":
            guide = True
        if r == "quit":
            run = False
    for obj in menu_group:
        obj.dis()
    pygame.display.update()
    CLOCK.tick(FPS)
    #screen
    while guide:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
                guide = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for obj in guide_group:
                        if obj.name == "button":
                            r = obj.tick(mouse_pos)
                            if r != None:
                                break
            if r == "back":
                guide = False
        for obj in guide_group:
            obj.dis()
        pygame.display.update()
        CLOCK.tick(FPS)
    while credit:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
                credit = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for obj in credit_group:
                        if obj.name == "button":
                            r = obj.tick(mouse_pos)
                            if r != None:
                                break
            if r == "back":
                credit = False
        for obj in credit_group:
            obj.dis()
        pygame.display.update()
        CLOCK.tick(FPS)
    while score:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
                score = False
            if event.type == pygame.MOUSEWHEEL:
                score_board.scroll(event.y)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for obj in score_group:
                        if obj.name == "button":
                            r = obj.tick(mouse_pos)
                            if r != None:
                                break
            if r == "back":
                score = False
        for obj in score_group:
            obj.dis()
        Screen.blit(score_board.get_score(),[200,90])
        pygame.display.update()
        CLOCK.tick(FPS)
    if game:
        keypress = {"119":False,"97":False,"115":False,"100":False,"114":False,"1073742049":False,"1073742048":False}
        p = Player("player",assets["player"],20,True)
        condition = {"space time":0,"walk":False,"speed":2,"destory":0,"tp":0,"find":False,"search":0,"help":0,"invi":0,"invib":False,"grow":False,"dive":False,"swim":False,"revive":False,"immo":False,"save":False,"respect":False,"doubt":False}
        enter_pos = [1,250]
        game_time = 0
        end = True
        while True:
            game_time += 1
            if game_time > 10800:
                break
            switch = False
            under = False
            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()
            ##event detection
            for event in events:
                #print(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == 102:
                        if condition["respect"] == False:
                            condition["respect"] = True
                            add_notice("Paying respect",notice_board)
                    if event.key == 120:
                        if condition["doubt"] == False:
                            condition["doubt"] = True
                            add_notice("doubt",notice_board)
                    #jump
                    if event.key == 32:
                        if condition["space time"] < 9:
                            condition["space time"] += 1
                        elif condition["space time"] == 9:
                            add_notice("New ability: jumping",notice_board)
                            p.up()
                            condition["space time"] += 1
                        else:
                            p.up()
                    #move
                    if str(event.key) in keypress.keys():
                        keypress[str(event.key)] = True
                        if condition["walk"] == False and str(event.key) in list(keypress.keys())[:4]:
                            condition["walk"] = True
                            add_notice("New ability: walking",notice_board)
                        if keypress["1073742049"]==True and (keypress["100"]==True or keypress["115"]==True or keypress["119"]==True or keypress["97"]==True) and condition["speed"] == 2:
                            condition["speed"] = 3
                            add_notice("New ability: running",notice_board)
                        if keypress["114"]==True and keypress["1073742049"]==True and (keypress["100"]==True or keypress["115"]==True or keypress["119"]==True or keypress["97"]==True) and condition["speed"] == 3:
                            condition["speed"] = 4
                            add_notice("New ability: sprinting",notice_board)
                    #search
                    if event.key == 113:
                        if condition["search"] == 5:
                            map.unhide()
                        elif condition["search"] == 4:
                            map.unhide()
                            condition["search"] += 1
                            add_notice("New ability: spider sense",notice_board)
                        elif condition["search"] < 4:
                            condition["search"] += 1
                if event.type == pygame.KEYUP:
                    if str(event.key) in keypress.keys():
                        keypress[str(event.key)] = False   
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if condition["destory"] > 19:
                            if map.collide_pt([mouse_pos],[2]) != None:
                                map.kick(map.collide_pt([mouse_pos],[2]))
                        elif condition["destory"] == 19:
                            add_notice("New abiltiy: destruction",notice_board)
                            if map.collide_pt([mouse_pos],[2]) != None:
                                map.kick(map.collide_pt([mouse_pos],[2]))
                                condition["destory"] += 1
                        elif map.collide_pt([mouse_pos],[2]) != None:
                            condition["destory"] += 1
                    if event.button == 3:
                        m_pos = [mouse_pos[0]-20,mouse_pos[1]-20]
                        if condition["tp"] > 19:
                            if map.collide_rect([pygame.Rect(m_pos[0],m_pos[1],40,40)],[1,2,3]) == None:
                                p.pos = list(m_pos)
                                map.add_obj([Object("effect",assets["tp"],30,False,[m_pos[0]-1,m_pos[1]-1],[],4)])
                        elif condition["tp"] == 19:
                            add_notice("New ability: teleportation",notice_board)
                            if map.collide_rect([pygame.Rect(m_pos[0],m_pos[1],40,40)],[1,2,3]) == None:
                                p.pos = list(m_pos)
                                map.add_obj([Object("effect",assets["tp"],30,False,[m_pos[0]-1,m_pos[1]-1],[],4)])
                                condition["tp"] += 1
                        elif map.collide_rect([pygame.Rect(m_pos[0],m_pos[1],40,40)],[1,2,3]) == None:
                            condition["tp"] += 1
                #quit
                if event.type == pygame.QUIT:
                    run = False
                    end = False
            #invi
            if keypress["1073742049"]:
                if condition["invib"]:
                    p.stats["invi"] = True
                elif condition["invi"] > 300:
                    p.stats["invi"] = True
                    if condition["invib"] == False:
                        condition["invib"] = True
                        add_notice("New ability: invisibility",notice_board)
                else:
                    condition["invi"] += 1
            else:
                condition["invi"] = 0
            #movement check
            dir = [0,0]
            if True:
                if keypress["119"]:
                    dir[1] -= 1
                if keypress["97"]:
                    dir[0] -= 1
                if keypress["115"]:
                    dir[1] += 1
                if keypress["100"]:
                    dir[0] += 1
                for t in range(condition["speed"]):
                    current = copy.deepcopy(p.pos)
                    new1 = [current[0]+dir[0],current[1]]
                    new2 = [current[0],current[1]+dir[1]]
                    new3 = [current[0]+dir[0],current[1]+dir[1]]
                    new_box1 = pygame.Rect(new1[0]+5,new1[1],30,40)
                    new_box2 = pygame.Rect(new2[0]+5,new2[1],30,40)
                    new_box3 = pygame.Rect(new3[0]+5,new3[1],30,40)
                    out = None
                    col_list = [1,2,3]
                    if p.stats["jump"] > 0:
                        col_list.remove(1)
                    if map.collide_rect([new_box3],col_list) == None:
                        p.move(dir)
                    else:
                        out = map.collide_rect([new_box3],col_list)
                        if map.collide_rect([new_box1],col_list) == None:
                            p.move([dir[0],0])
                        if map.collide_rect([new_box2],col_list) == None:
                            p.move([0,dir[1]])
                    if map.collide_rect([new_box3],[5]) != None:
                        if condition["swim"] == False:
                            condition["swim"] = True
                            add_notice("New ability: swimming",notice_board)
                        p.stats["swim"] = True
                        if map.collide_rect([new_box3],[5]).name == "river" and keypress["1073742048"]:
                            switch = True
                            under = True
                    if map.collide_rect([new_box3],[6]) != None:
                        if map.collide_rect([new_box3],[6]).kill and condition["immo"] == False:
                                p.pos = copy.deepcopy(enter_pos)
                                load_screen()
                                if condition["revive"] == False:
                                    condition["revive"] = True
                                    add_notice("New ability: revival",notice_board)
                                break
                    if out != None:
                        if out.name == "shop":
                            if condition["speed"] != 5:
                                condition["speed"] = 5
                                add_notice("New abiltiy: coffee",notice_board)
                        elif "item" in out.name:
                            if condition["find"]:
                                p.add_to_inv(out.name)
                                map.kick(out)
                            else:
                                condition["find"] = True
                                add_notice("New ability: lost and found",notice_board)
                                p.add_to_inv(out.name)
                                map.kick(out)
                        elif "NPC" in out.name:
                            for item in p.stats["inv"]:
                                if item == out.need:
                                    p.stats["inv"].remove(item)
                                    out.need = None
                                    condition["help"] += 1
                                    map.add_obj([Object("heart",[assets["heart"]],120,False,[out.pos[0]+10,out.pos[1]+10],[],4)])
                                    if condition["help"] == 1:
                                        add_notice("New ability: helping hand",notice_board)
                        elif "plant" in out.name:
                            out.age += 1
                            if out.age >= 300 and condition["grow"] == False:
                                condition["grow"] = True
                                out.grow()
                                add_notice("New ability: mother nature",notice_board)
                            elif out.age >= 300:
                                out.grow()
                        elif "enemy" in out.name:
                            if out.kill and condition["immo"] == False:
                                p.pos = copy.deepcopy(enter_pos)
                                load_screen()
                                if condition["revive"] == False:
                                    condition["revive"] = True
                                    add_notice("New ability: revival",notice_board)
                                break
                            elif out.kill and condition["immo"] and out.savable:
                                map.add_obj([Object("heart",[assets["heart"]],120,False,[out.pos[0]+10,out.pos[1]+10],[],4)])
                                if condition["save"] == False:
                                    condition["save"] = True
                                    add_notice("New ability: justice",notice_board)
                                out.kill = False
                        elif out.name == "tip":
                            add_notice(out.content,notice_board)
                            map.kick(out)
                        elif out.name == "life":
                            if condition["immo"] == False:
                                condition["immo"] = True
                                add_notice("New ability: immotarlity",notice_board)
                            map.kick(out)
            #switch     
            check_res =  location_check(p)
            if check_res != None:
                switch = True
                enter_pos = copy.deepcopy(check_res)
            ##clean up
            refresh(map,p,notice_board)
            if switch:
                load_screen()
                map = Objects()
                map.add_obj(map_gen(under,p.pos))
                if under:
                    if condition["dive"] == False:
                        condition["dive"] = True
                        add_notice("New abiltiy: diving",notice_board)
            CLOCK.tick(FPS)
            #quit
            if run == False:
                break  
        map = Objects()
        map.add_obj(map_gen(False,[2,250]))
        while end: 
            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                    end = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for obj in end_group:
                            if obj.name == "button":
                                r = obj.tick(mouse_pos)
                                if r != None:
                                    break
                if r == "yes":
                    res = ["18 Abilities in total:"]
                    if condition["walk"]:
                        res.append("walking")
                    if condition["speed"] == 3:
                        res.append("running")
                    if condition["speed"] == 4:
                        res.append("running")
                        res.append("sprinting")
                    if condition["speed"] == 5:
                        res.append("running")
                        res.append("sprinting")
                        res.append("coffee")
                    if condition["space time"] > 8:
                        res.append("jumping")
                    if condition["tp"] > 18:
                        res.append("teleportation")
                    if condition["destory"] > 18:
                        res.append("destruction")
                    if condition["swim"]:
                        res.append("swimming")
                    if condition["dive"]:
                        res.append("diving")
                    if condition["invib"]:
                        res.append("invisibility")
                    if condition["revive"]:
                        res.append("revival")
                    if condition["immo"]:
                        res.append("immortality")
                    if condition["search"] > 3:
                        res.append("spider sense")
                    if condition["grow"]:
                        res.append("mother nature")
                    if condition["help"] > 0:
                        res.append("helping hand")
                    if condition["save"]:
                        res.append("justice")
                    if condition["doubt"]:
                        res.append("press x to doubt")
                    if condition["respect"]:
                        res.append("press f to pay respect")
                    with open("data/game_data.csv","w") as data:
                        data = csv.writer(data,delimiter = ",")
                        data.writerow(res)
                    score_board = Score_board(get_list())
                    end = False
                if r == "no":
                    end = False
            for obj in end_group:
                obj.dis()
            pygame.display.update()
            CLOCK.tick(FPS)