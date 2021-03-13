import pygame
import sys
import random
import os

# 节点类
class Point(object):
    def __init__(self,row=0,col=0,color=(0,80,0)):
        self.x = row
        self.y = col
        self.color = color

# 蛇类
class snake(object):
    
    def __init__(self):
        self.x = 15 # 蛇头x坐标
        self.y = 15 # 蛇头y坐标
        self.color = (0, 255, 0) # 蛇头颜色
        self.body = [Point(self.x,self.y + 1)] # 蛇身list
    
    # 蛇身移动函数
    def move(self):
        self.body.insert(0, Point(self.x, self.y))
        self.body.pop()
    
    # 向下状态
    def down(self):
        self.move()
        self.y = self.y + 1

    # 向上状态
    def top(self):
        self.move()
        self.y = self.y - 1

    # 向左状态
    def left(self):
        self.move()
        self.x = self.x - 1
        

    # 向右状态
    def right(self):
        self.move()
        self.x = self.x + 1
        
    # 死亡状态
    def dead(self):
        print('Game Over')

    # 生长状态
    def graw(self):
        self.body.insert(0, Point(self.x, self.y)) # 不弹出尾巴节点


    # 将蛇类对象与FSM类对象链接起来，并给予蛇类状态
    def attach_fsm(self, state, fsm):
        self.fsm = fsm
        self.curr_state = state

    # 改变蛇的状态
    def change_state(self, new_state, new_fsm):
        self.curr_state = new_state # 切换状态
        self.fsm.exit_state(self) # 离开原来状态动作
        self.fsm = new_fsm  # 切换FSM
        self.fsm.enter_state(self) # 进入新的状态动作
        self.fsm.exec_state(self) # 维持新的状态动作

    # 蛇保持状态
    def keep_state(self):
        self.fsm.exec_state(self)

# FSM纯虚接口类
class base_fsm(object):

    # 进入动作
    def enter_state(self, obj):
        raise NotImplementedError()

    # 保持动作
    def exec_state(self, obj):
        raise NotImplementedError()
    
    # 离开动作
    def exit_state(self, obj):
        raise NotImplementedError()

# 向下状态类
class down_fsm(base_fsm):
    def enter_state(self, obj):
        print('your snake enter down state!')

    def exec_state(self, obj):
        obj.down()

    def exit_state(self, obj):
        print('your snake exit down state!')

# 向上状态类
class top_fsm(base_fsm):
    def enter_state(self, obj):
        print('your snake enter top state!')

    def exec_state(self, obj):
        obj.top()

    def exit_state(self, obj):
        print('your snake exit top state!')
    
# 向左状态类
class left_fsm(base_fsm):
    def enter_state(self, obj):
        print('your snake enter left state!')

    def exec_state(self, obj):
        obj.left()

    def exit_state(self, obj):
        print('your snake exit left state!')

# 向右状态类
class right_fsm(base_fsm):
    def enter_state(self, obj):
        print('your snake enter right state!')

    def exec_state(self, obj):
        obj.right()

    def exit_state(self, obj):
        print('your snake exit right state!')

# 死亡状态类
class dead_fsm(base_fsm):
    def enter_state(self, obj):
        print('your snake enter dead state!')

    def exec_state(self, obj):
        obj.dead()

    def exit_state(self, obj):
        print('your snake exit dead state!')

# 生长状态类
class graw_fsm(base_fsm):
    def enter_state(self, obj):
        print('your snake enter graw state!')

    def exec_state(self, obj):
        obj.graw()

    def exit_state(self, obj):
        print('your snake exit graw state!')

# FSM类
class fsm_mgr(object):

    def __init__(self):
        self._fsms = {} # 状态dic
        self._fsms[0] = down_fsm()
        self._fsms[1] = top_fsm()
        self._fsms[2] = left_fsm()
        self._fsms[3] = right_fsm()
        self._fsms[4] = dead_fsm()
        self._fsms[5] = graw_fsm()

    # 返回state对应的状态
    def get_fsm(self, state):
        return self._fsms[state]

    # 根据对象现在的状态和当前的输入决定让对象保持状态或者改变状态
    def work(self, objs, state, last_state):
        for obj in objs:
            if state == obj.curr_state:
                obj.keep_state()
            # 生长状态比较特殊，单独判断
            elif state == 5:
                # 先变为生长状态，生长完成再变为原来的状态
                obj.change_state(state, self._fsms[state])
                obj.change_state(last_state, self._fsms[last_state])    
            else:
                obj.change_state(state, self._fsms[state])
                
# 世界类
class World(object):
    
    def init(self):
        self._snakes = [] #蛇list   
        self._fsm_mgr = fsm_mgr() #FSM对象
        self.__init_snake()  # 产生蛇
        self.key = 1  # 当前状态
        self.key0 = 1 # 上一个状态
        self.last = -1 # 上一个按键
        self.height = 800 # 窗口高度
        self.width = 800 # 窗口宽度
        self.Num_Of_Row = 30  # 行数
        self.Num_Of_Col = 30  # 列数
        self.f = 10 # 刷新频率
        self.eat = 0 # 蛇是否进食判断变量
        self.Food = self.gen_food() # 食物节点
        self.dead = 0 # 游戏结束判断变量
        self.score = 0 # 得分变量

    def __init_snake(self):
        tmp = snake() 
        tmp.attach_fsm(1, self._fsm_mgr.get_fsm(1)) #初始化汽车状态为1，把1对应的fsm给汽车
        self._snakes.append(tmp) #世界的汽车列表中加入这个汽车

    # 驱动FSM
    def __work(self, key, key0):
        self._fsm_mgr.work(self._snakes, key, key0)
        
    # 生成食物
    def gen_food(self):
        while 1:
            # 随机生成一个食物坐标
            position = Point(random.randint(0, self.Num_Of_Row - 1), random.randint(0, self.Num_Of_Row - 1),(255,0,0))
            # 判断食物是否和蛇身体重合
            is_ok = False
            for _snake in self._snakes:
                if _snake.x == position.x and _snake.y == position.y:
                    is_ok = True
                for section in _snake.body:
                    if section.x == position.x and section.y == position.y:
                        is_ok = True
                        break
            if not is_ok:
                break
        return position # 返回食物坐标

    # 绘图函数，可以将对应位置的单元格染色
    def rect(self, obj, window):
        top = obj.y * self.width / self.Num_Of_Col
        left = obj.x * self.height / self.Num_Of_Row
        # 将方块涂色
        pygame.draw.rect(window, obj.color, (left, top,  self.width / self.Num_Of_Col,  self.height / self.Num_Of_Row))
    
    # 世界运行函数
    def run(self):
        
        pygame.init()  # 初始化pygame
        window = pygame.display.set_mode((world.height, world.width))  # 显示窗口
        clock = pygame.time.Clock()  # 设置时钟
        pygame.display.set_caption('Greedy snake based on FSM') # 窗口命名
        
        while True:
            clock.tick(self.f)  # 每秒执行f次

            for event in pygame.event.get():  # 遍历所有事件
                if event.type == pygame.QUIT:  # 如果单击关闭窗口，则退出
                    sys.exit()
                elif event.type == pygame.KEYDOWN: # 键盘事件
                    # 如果按下w，而且现在不是s
                    if event.key == pygame.K_w and self.key != 0:
                        self.key0 = self.key # 更新上一次状态为当前状态
                        self.key = 1 # 当前状态转换
                        if self.last == pygame.K_w: #如果上次也按了w，那么就加速，下同
                            self.f = 20
                            self.last = -1
                        else: # 再按一次w取消加速，下同
                            self.f = 10
                            self.last = pygame.K_w
                    # 如果按下s，而且现在不是w
                    elif event.key == pygame.K_s and self.key != 1:
                        self.key0 = self.key
                        self.key = 0
                        if self.last == pygame.K_s:
                            self.f = 20
                            self.last = -1
                        else:
                            self.f = 10
                            self.last = pygame.K_s
                    # 如果按下a，而且现在不是d
                    elif event.key == pygame.K_a and self.key != 3:
                        self.key0 = self.key
                        self.key = 2
                        if self.last == pygame.K_a:
                            self.f = 20
                            self.last = -1
                        else:
                            self.f = 10
                            self.last = pygame.K_a
                    # 如果按下d，而且现在不是a
                    elif event.key == pygame.K_d and self.key != 2:
                        self.key0 = self.key
                        self.key = 3
                        if self.last == pygame.K_d:
                            self.f = 20
                            self.last = -1
                        else:
                            self.f = 10
                            self.last = pygame.K_d
            
            # 如果游戏没有结束
            if not self.dead:
                
                # 画背景
                pygame.draw.rect(window, (0, 0, 0), (0, 0, self.width, self.height))
                ft = pygame.font.SysFont("arial", 32)
                name = ft.render("By Cao Jianing", True, (120, 120, 120))
                ver = ft.render("version: 1.0", True, (120, 120, 120))
                window.blit(name, (5, 0))
                window.blit(ver, (25, 32))

                # 画蛇和食物
                self.rect(self.Food,window)
                for _snake in self._snakes:
                    self.rect(_snake,window)
                    for section in _snake.body:
                        self.rect(section,window)
                
                #判断是否吃到食物
                for _snake in self._snakes:
                    self.eat = (_snake.x == self.Food.x and _snake.y == self.Food.y)
                    if self.eat:
                        self.key0 = self.key
                        self.key = 5
                        self.score = self.score + 1
                        self.Food = self.gen_food()    
                        break
                
                # 驱动FSM运行
                self.__work(self.key, self.key0)

                # 判断是否咬到自己或者撞墙
                for _snake in self._snakes:
                    if _snake.x < 0 or _snake.y < 0 or _snake.x >= self.Num_Of_Col or _snake.y >= self.Num_Of_Row:
                        self.dead = True
                        self.key = 4
                        break
                    for section in _snake.body:
                        if _snake.x == section.x and _snake.y == section.y:
                            self.dead = True
                            self.key = 4
                            break
                
                # 生长状态只运行一次
                if self.key == 5:
                    self.key = self.key0

            # 如果游戏结束                
            else:
                ft = pygame.font.SysFont("arial", 64)
                text1 = ft.render("Game Over", True, (255, 255, 255))
                text2 = ft.render("Score:  "+str(self.score), True, (255, 255, 0 ))
                window.blit(text1, (270, 300))
                window.blit(text2, (290, 400))
                # dog = pygame.image.load('1.jpg')  # 加载图片
                # dog = pygame.transform.scale(dog, (200,200)) #缩放为x=100，y=200
                # window.blit(dog, (300, 500))  # 将图片画到窗口上
            
            # 更新显示
            pygame.display.flip()

        pygame.quit()  # 退出pygame

if __name__ == '__main__':
    world = World() # 创建world对象
    world.init() # 初始化世界
    world.run() # 运行世界