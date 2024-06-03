from build_tree import BuildAST
import operator as op

from get_token import get_token


# 执行语法树的时候需要运行环境
class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.update(zip(params, args))  # 将参数信息保存到环境中
        self.outer = outer

    # 寻找环境的值， 找不到会继续往外层去寻找值
    def find(self, key):
        return self if key in self else self.outer


def build_stand_env():
    env = Env()
    import math
    env.update(vars(math))
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.floordiv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        '%': op.mod
    })
    return env


stand_env = build_stand_env()


# 定义一个新的保留字 fun, 用来定义一个匿名函数
class Fun:
    def __init__(self, params, body, env_: Env):
        self.params = params
        self.body = body
        self.env = env_

    def __call__(self, *args, **kwargs):
        return ExecStr.eval_(self.body, Env(self.params, args, self.env))


# 执行构造出来的语法树
class ExecStr:
    def __init__(self, s: str):
        ast = BuildAST(get_token(s))
        self.ast = ast.build_ast()

    @staticmethod
    def eval_(x, env: Env):
        # 如果是变量， 返回变量的值
        if isinstance(x, str):
            tmp = env.find(x)
            if tmp:
                return tmp[x]
            else:
                raise Exception("变量{}未定义".format(x))
        # 不是列表，不是变量，就是常量
        elif not isinstance(x, list):
            return x
        cmd = x[0]
        if cmd == 'if':
            _, test, val1, val2 = x
            if ExecStr.eval_(test, env):
                return ExecStr.eval_(val1, env)
            return ExecStr.eval_(val2, env)
        elif cmd == 'define':
            _, var_name, var = x
            env.update({var_name: ExecStr.eval_(var, env)})
        elif cmd == 'lambda':
            _, args, body = x
            return Fun(args, body, env)
        else:
            fun = ExecStr.eval_(cmd, env)
            args = [ExecStr.eval_(expr, env) for expr in x[1:]]
            return fun(*args)


if __name__ == '__main__':
    exec_ = ExecStr("(define r 10)")
    env = build_stand_env()
    exec_.eval_(exec_.ast, env)
    ast = BuildAST(get_token("(* pi (* r r))"))
    print(exec_.eval_(ast.build_ast(), env))
    ast = BuildAST(get_token("(define circle-area (lambda (r) (* pi (* r r))))"))
    exec_.eval_(ast.build_ast(), env)
    ast = BuildAST(get_token("(circle-area 20)"))
    print(exec_.eval_(ast.build_ast(), env))
