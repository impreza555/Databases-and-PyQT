import dis


class ServerMaker(type):
    def __init__(cls, cls_name, parents, cls_dict):
        methods = []
        attrs = []
        for func in cls_dict:
            try:
                instruction = dis.get_instructions(cls_dict[func])
            except TypeError:
                pass
            else:
                for i in instruction:
                    # print(i)
                    if i.opname in ('LOAD_GLOBAL', 'LOAD_METHOD'):
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(cls_name, parents, cls_dict)


class ClientMaker(type):
    def __init__(cls, cls_name, bases, cls_dict):
        methods = []
        for func in cls_dict:
            try:
                instruction = dis.get_instructions(cls_dict[func])
            except TypeError:
                pass
            else:
                for i in instruction:
                    # print(i)
                    if i.opname in ('LOAD_GLOBAL', 'LOAD_METHOD'):
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        if 'getting' in methods or 'sending' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(cls_name, bases, cls_dict)
