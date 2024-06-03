# 简单的检查一下，括号匹配是否成功
def judge(s: str):
    stack = []
    for i in s:
        if i == '(':
            stack.append(i)
        elif i == ')':
            if stack and stack[-1] == '(':
                stack.pop()
            else:
                raise Exception("括号匹配失败")
    if len(stack) != 0:
        raise Exception("括号匹配失败")


# 该文件用来读取字符串，将字符串拆分为一个个的token
def get_token(s: str) -> list:
    judge(s)
    # 将括号替换为 空格加括号的组合，方便字符串的分割
    tokens = s.replace('(', ' ( ').replace(')', ' ) ').split()
    return tokens


if __name__ == '__main__':
    get_token("(q23esw())")
