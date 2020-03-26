# class A:
#     def __init__(self,value):
#         self.value = value

#     def __str__(self):
#         return str(self.value)
# a = A(2)
# # b = A(3)
# # c = A(4)
# # l = [a,b,c]

# # l.remove(b)
# # [print(i) for i in l]

# class B(A):
#     def __init__(self,value):
#         super().__init__(value)

#     def func(self,value):
#         print('Hello', value)


# class C(A):
#     def __init__(self,value):
#         super().__init__(value)

#     def func(self,value):
#         print('Hello', value)

# smap = {'a':'func'}

# b = B(2)
# c = C(3)
# # if isinstance(c, A):
# #     print('Hello')
# # if isinstance(b,A):
# #     print('Hello')

# if isinstance(b, C):
#     print('Hello')


# b.__getattribute__(smap['a'])(1)

class X:
    def __init__(self):
        self.li = []
        self.curr = len(self.li)

    def addElements(self, value):
        self.li.append(value)

    def currLen(self):
        return len(self.li)

x = X()    
print(x.curr)
print(x.currLen())
x.addElements(2)
print(x.curr)
print(x.currLen())
x.addElements(4)
print(x.curr)
print(x.currLen())
