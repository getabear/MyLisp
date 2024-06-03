################ python3 实现 lisp 解释器
'''
语言的语法是指组成正确的语句或表达式的顺序，语义指那些表达式或语句的内在含义。
解释器流程
程序 => 解析 => 抽象语法树 => 执行(语义) => 结果
1:解析语法
2:添加环境
3:执行
4:添加交互式
5: 将Env重定义为Class
6:添加符合Schema的语法形式(quote，set!，lambda)
其实还有一个begin，它是按从左到右的顺序对表达式进行求值，并返回最终的结果，但是已经在环境中定义了
'''

# from __future__ import division
import math, sys, re
import operator as op

################ 类型

Symbol = str  # 字符串
List = list  # 列表
Number = (int, float)  # 数字


# Env = dict  # 环境

# ======= 第一步 解析语法 =======

# ======== 解析语法 ========
def parse(program):
    '''
    语法解析函数
    参数：语句字符串
    返回：抽象语法树，多维数组形式展示嵌套关系
    '''
    return read_from_tokens(tokenize(program))


def tokenize(s):
    '''
    字符串转list
    词法分析：也就是将输入字符串分成一系列 token，返回一个语法列表
    参数：语句字符串
    返回：一个简单的语法列表，tokens
    '''
    # 默认空格分隔。所以需要将括号添加空格，以便分隔出来
    tokens = s.replace('(', ' ( ').replace(')', ' ) ').split()
    # 判断括号对
    if tokens.count('(') != tokens.count(')'):
        print('括号对不一致！')
        return
    return tokens


def read_from_tokens(tokens):
    '''
    解析list
    语义分析：将tokens组装成抽象语法树
    参数：语法列表
    返回：抽象语法树列表
    如果tokens长度为零直接返回
    去掉tokens第一个字符
    如果第一个字符是（ ，定义一个空列表用来存放语法树，如果tokens第一个字符不是 ），循环将同级语法树存到列表，碰到 ）直接去掉，返回这一层语法树
    其它情况返回字符，如果是数字就返回数字，其它的返回字符串
    '''
    if not isinstance(tokens, List):
        return

    if len(tokens) == 0:
        print('不能为空')
        return

    # list去掉第一位元素，如果不是（ 就将它转换类型后加入列表中
    token = tokens.pop(0)
    # 第一个字符是(，然后建立表达式列表，直到匹配到 ）
    if '(' == token:
        # 这里定义空list是为了抽象语法树的嵌套关系
        L = []
        # 语法树第一个字符是）一定是错误语法
        while tokens[0] != ')':
            # 将括号以外的字符加进list中
            # 这里的递归是为了用多维数组展示抽象语法树的嵌套关系，同级的字符放在一个list中
            token_key = read_from_tokens(tokens)
            L.append(token_key)
        # 删除括号结束符 ）,如果不删除的话，碰到 ）就无法循环下去，只能得到部分语法树
        tokens.pop(0)
        # 返回同级数据
        return L
    elif ')' == token:
        print('语法错误')
    else:
        # 返回字符，如果数字转成整数或者浮点类型，其它都是字符串
        return atom(token)


def atom(token):
    '''
    字符串类型转换
    Lispy 的 tokens 是括号、标识符和数字
    '''
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


# python3 不存在apply，所以这里自己定义一个
def apply(func, *args, **kwargs):
    return func(*args, **kwargs)


def _add(*datas):
    # 加法，支持多数字，多字符串 (+ 1 2 3 4)，(+ "a" "b" "c")
    if len(datas) > 0:
        if isinstance(datas[0], int) or isinstance(datas[0], float):
            sum_num = 0
            for data in datas:
                sum_num = sum_num + data
            return sum_num
        if isinstance(datas[0], str):
            sum_num = ""
            for data in datas:
                sum_num = sum_num + data.replace('\"', '')
            return '\"' + sum_num + '\"'


def _sub(*datas):
    # 减法，支持多数字 (- 9 2 1)
    sub_num = 0
    for data in datas:
        if len(datas) > 1 and sub_num == 0:
            sub_num = data
        else:
            sub_num = sub_num - data
    return sub_num


def _mul(*datas):
    # 乘法，支持多数字 (* 2 3 4)
    mul_num = 1
    for data in datas:
        mul_num = data * mul_num
    return mul_num


def _truediv(*datas):
    # 除法，支持多数字 (/ 8 4 2)
    truediv_num = 1
    for data in datas:
        if truediv_num == 1:
            truediv_num = data
        else:
            truediv_num = truediv_num / data
    return truediv_num


def _to_char(char_data):
    # char 转化 字符 #\a，字符 a，判断是否是char
    if isinstance(char_data, str):
        pattern = re.compile(r'(^#\\)([\S]{1})')
        match = pattern.search(char_data)
        if match:
            return char_data


def _to_string(str_data):
    # string 转化 字符串 "aa"，判断是否是字符串
    # 字符串，为了显示区分添加"
    if isinstance(str_data, str):
        pattern = re.compile(r'(^\")(\S*)(\"$)')
        match = pattern.search(str_data)
        if match:
            return str_data


def _map(fn, *datas):
    # python3的map返回一个迭代器，所以这里需要处理一下，返回list
    datas = map(fn, *datas)
    new_datas = []
    # for data in datas:
    #     new_datas.append(data)
    try:
        while True:
            line = next(datas)
            if line is None:
                break
            new_datas.append(line)
    except StopIteration:
        pass
    return new_datas


# ====== 第五步 重定义环境 =========

# ====== 将Env环境定义成class =======
class Env(dict):
    '''
    Env继承dict类
    '''

    def __init__(self, parms=(), args=(), outer=None):
        # 构造函数
        # 初始化环境，zip可以直接转化成dict
        self.update(zip(parms, args))
        # 全局环境
        self.outer = outer

    def find(self, var):
        # 查找环境，这个是为了后面的局部环境和全局环境
        # 如果存在在局部环境中返回局部环境，没有就去全局环境找
        return self if (var in self) else self.outer.find(var)


class Procedure(object):
    '''
    这个可以看作一个创造局部环境和外部环境的函数
    '''

    def __init__(self, parms, body, env):
        # 构造函数
        '''
        parms 是参数名
        body 是表达式
        env 是外部环境
        '''
        self.parms = parms
        self.body = body
        self.env = env

    def __call__(self, *args):
        # 调用对象的时候执行
        '''
        执行表达式，但是将上层的环境当作外部环境，将这一层的参数名与实际值设置为局部环境
        '''
        return eval(self.body, Env(self.parms, args, self.env))


# ======= 第二步 设置环境 =======

# ====== 环境 =======
'''
环境是指变量名与值之间的映射。eval 默认使用全局环境，包括一组标准函数的名称（如 sqrt 和 max，以及操作符 *）
'''


def standard_env():
    '''
    简单的标准环境
    环境是一个字典形式，将环境中添加标准库，或者自己定义的函数
    '''
    env = Env()  # 环境是一个字典形式
    # vars函数是python自带函数 返回对象object的属性名和属性值的字典形式
    env.update(vars(math))  # sin, cos, sqrt, pi, ...
    # 添加一些符合Scheme标准的环境
    env.update({
        # '+':op.add,
        # '-':op.sub,
        # '*':op.mul,
        # '/':op.truediv,
        '+': _add,
        '-': _sub,
        '*': _mul,
        '/': _truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        '%': op.mod,
        # 'add': op.add,
        # 'sub': op.sub,
        # 'mul': op.mul,
        # 'truediv': op.truediv,
        # 'add': _add,
        # 'sub': _sub,
        # 'mul': _mul,
        # 'truediv': _truediv,
        'mod': op.mod,
        'abs': abs,
        'append': op.add,
        'apply': apply,
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y if isinstance(y, List) else [x] + [y],
        'eq?': op.is_,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: List(x),
        'list?': lambda x: isinstance(x, List),
        'map': _map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol),
        '#t': True,
        '#f': False,
        # (vector 1 "2" 3 "4") 类似列表的，我就用列表表示了
        # 'vector': lambda *x: '#'+schemestr(list(x)),
        'boolean?': lambda x: True if x else False,
        'string?': lambda x: True if _to_string(x) else False,
        'char?': lambda x: True if _to_char(x) else False,
        # 'display': print

    })
    # 返回这个环境
    return env


# 作为全局环境
global_env = standard_env()


# ======= 第三步 执行 ========

# ======= 执行 ========
def eval(x, env=global_env):
    '''
    执行语义
    如果是字符，去环境中查找变量值或者函数
    如果是数字直接输出
    如果第一个字符是if先递归计算判断条件的值，然后递归计算输出值
    如果第一个字符是define递归计算出值，然后加入环境中
    其它的情况先用第一个字符去环境中查找函数，然后递归将后面的字符存入列表，最后执行函数参数是之前列表
    if 语句：
        (if test conseq alt)
        test是判断条件，如果符合输出conseq，否则输出alt
        例子：
            (if (> 1 0) 1 0)
            (if (> 1 0) (+ 1 2) (- 9 3))
    define 语句：
        (define symbol exp)
        例子：
            (define x 1)
    quote 语句：
        (quote exp)
        例子：
            (quote (1 2 3))
    set! 语句：
        (set! var exp)
        例子：
            (set! x 1)
            注意：set! 是修改已经定义的变量，没有定义就使用会报错
    lambda 语句：
        (lambda (var...) body)
        例子：
            (lambda (x) (+ x x))
            注意：lambda 匿名函数需要定义以后使用 (define xx (lambda (x) (+ x x)))，用(xx 4)方式调用
    let 语句：
        (let ((var val) ...) exp)
        例子：
            (let ((f +) (x 2)) (f x 3)) 其实就是把加法赋值给f，把3赋值给x，然后计算
            (let ((x 2) (y 3)) (+ x y)) x=2，y=3，x+y
            (let ((double (lambda (x) (+ x x))))(list (double (* 3 4))(double (/ 99 11))(double (- 2 7))))
    begin 语句：
        (degin exp....)
        例子：
            (define x 1)
            (begin (set! x 1) (set! x (+ x 1)) (* x 2))
    display 语句：
        例子：
            (display "a") 相当于python的print
    实现python的range函数：
        例子：
            (define range (lambda (a b) (if (= a b) (quote ()) (cons a (range (+ a 1) b)))))
            (range 0 10)
            注意：Scheme 没有for，whlie，所以循环用递归代替
    map 语句：
        例子：
            (define fib (lambda (n) (if (< n 2) 1 (+ (fib (- n 1)) (fib (- n 2))))))
            (define range (lambda (a b) (if (= a b) (quote ()) (cons a (range (+ a 1) b)))))
            (map fib (range 0 20))
    list ：
        例子 (list 1 2 3 4)
    实现python中list的count函数：
        例子：
            (define count (lambda (item L) (if L (+ (equal? item (car L)) (count item (cdr L)))
            (count 0 (list 0 1 2 3 0 0))
    '''
    if isinstance(x, Symbol):
        # 字符 #\a，字符 a
        char_data = _to_char(x)
        if char_data:
            # 返回字符
            return char_data
        # 字符串，为了显示区分添加"
        str_data = _to_string(x)
        if str_data:
            # 返回字符串
            return str_data
        # 如果是字符就去环境中找，返回变量值或者函数
        # 这样可以根据调用去局部环境或者外部环境查找
        data = env.find(x)[x]
        return data
    # 常量返回
    elif not isinstance(x, List):
        return x
    elif x[0] == 'quote':
        # (quote exp)
        # (quote (1 2))
        (_, exp) = x
        # quote 就是原样输出表达式
        return exp
    # if 语句，形式(if test conseq alt),test是判断条件,符合条件输出conseq,不符合输出alt
    elif x[0] == 'if':
        # (if test conseq alt)
        # (if (> 1 2) 1 2)
        # 语句形式分别赋值
        (_, test, conseq, alt) = x
        # 用递归计算条件
        exp = (conseq if eval(test, env) else alt)
        # 判断后结果可能是表达式所以也用递归计算出值
        return eval(exp, env)
    # define 定义变量，形式(define symbol exp),sybol是变量，exp是值
    elif x[0] == 'define':
        # (define var exp)
        # (define x 1)
        (_, var, exp) = x
        # 用递归计算数据
        # 将定义的数据加进环境中
        # 用递归是因为如果exp是个表达式，就计算出它的值再加入环境
        env[var] = eval(exp, env)
    elif x[0] == 'set!':
        # (set! var exp)
        # (set! x 1)，注意这里的x必须先定义过，也就是环境中必须有
        (_, var, exp) = x
        # set! 其实是一个覆盖环境值的操作，用递归也是因为如果exp是个表达式，就计算出它的值再加入环境
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':
        # (lambda (var...) body)
        # (lambda (x) (+ x x))，这样其实无法调用，一般用(define xx (lambda (x) (+ x x))) 定义，(xx 3)调用
        (_, parms, body) = x
        '''
        这里就用到了Procedure类
        因为lambda匿名函数的参数都是局部的，外面是无法调用的，所以这里先保存参数名，表达式，将env当作外部环境(因为可能会用到外部环境的变量)
        当调用的时候将值传入，与参数名配对，当作局部环境
        '''
        return Procedure(parms, body, env)
    elif x[0] == 'let':
        # (let ((var val) ...) exp1 exp2 ...)
        (_, var, exp) = x
        # 将定义分别加进环境中
        for data in var:
            env[data[0]] = eval(data[1], env)
        # 最后执行
        return eval(exp, env)
    else:
        '''
        Schema 计算形式第一个元素是计算符号:(+ 1 2)
        '''
        # list第一个元素去环境里去找这个函数
        # (proc arg...)
        proc = eval(x[0], env)
        # list后面的元素是函数参数
        args = [eval(exp, env) for exp in x[1:]]
        # 将参数传入函数
        data = proc(*args)
        return data


# ======== 交互式 ========
def repl(prompt='lis.py> '):
    '''
    终端交互式，死循环读取终端输入字符串，执行，转换成字符串，打印到终端
    '''
    # 这里学习python的交互式加入提示
    sys.stderr.write('-*- lispy 0.01 -*- Quit using \'exit()\'\n')
    # 死循环读取终端输入
    while True:
        data_str = input(prompt)
        # 防止不输入程序报错
        if data_str:
            # python交互式一样，输入exit()结束程序
            if data_str == 'exit()':
                sys.exit()
            # 执行
            val = eval(parse(data_str))
            if val is not None:
                # 打印
                print(schemestr(val))


def schemestr(exp):
    """
    将数据转位字符串
    """
    if isinstance(exp, List):
        # 将列表中所有元素转成字符串，用空格分隔，开始结束加上括号
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    elif isinstance(exp, bool):
        # bool 转化 #t: true，#f: flase
        if exp:
            return '#t'
        else:
            return '#f'
    else:
        # 转成字符串
        return Symbol(exp)

if __name__ == "__main__":
    val = eval(parse("(define r 10)"))
    if val is not None:
        # 打印
        print(schemestr(val))