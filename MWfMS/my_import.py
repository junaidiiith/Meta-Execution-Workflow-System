def imp(name):

    __import__(name.rsplit('.',1)[0])
    components = name.split('.')
    mod = __import__(components[0])
    # print(mod)
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod