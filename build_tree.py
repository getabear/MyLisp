from get_token import get_token


class BuildAST:
    def __init__(self, tokens):
        if not isinstance(tokens, list):
            raise Exception("tokens 必须是一个列表")
        self.tokens = tokens
        self.idx = 0

    def atom(self, token):
        try:
            return int(token)           # 尝试将转换为整形
        except ValueError:
            try:
                return float(token)     # 尝试转换为浮点型
            except ValueError:
                return token            # 返回字符串， 相当于变量， 或字符串值

    # 用来构建一个语法树， 该树由列表组成
    def build_ast(self):
        # 懒得写self， 所以内部重新定义了build_函数
        def build_():
            ret = []
            if self.tokens[self.idx] == '(':
                self.idx += 1       # 跳过左括号
                while self.tokens[self.idx] != ')':
                    # 还是表达式
                    if self.tokens[self.idx] == '(':
                        ret.append(build_())
                        continue
                    # 是符号（关键字 变量 常量等）
                    else:
                        ret.append(self.atom(self.tokens[self.idx]))
                    self.idx += 1
                self.idx += 1       # 跳过右括号
                return ret
            elif self.tokens[self.idx] == ')':
                raise Exception("语法错误")
        return build_()


if __name__ == '__main__':
    tokens = get_token("(if (> 1 2) (add 1 3) (add 2 4))")
    a = BuildAST(tokens)
    print(a.build_ast())
