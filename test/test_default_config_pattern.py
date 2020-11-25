import exputils as eu


class MyMainClass():

    @staticmethod
    def default_config():
        dc = eu.AttrDict()
        dc.scalar = 1
        dc.string = 'my_string'
        return dc

    def __init__(self, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())
        self.my_attr = self.config.scalar


class MySubClass1(MyMainClass):

    @staticmethod
    def default_config():
        dc = MyMainClass.default_config()
        dc.scalar = 2
        dc.string2 = 'my_string2'
        return dc

    def __init__(self, config=None, **kwargs):
        super().__init__(config=config, **kwargs)


def test_config_pattern():

    main_class_obj = MyMainClass()
    assert (main_class_obj.my_attr == 1)
    assert (main_class_obj.config.scalar == 1)
    assert (main_class_obj.config.string == 'my_string')

    # subclass that keeps default config of main before overriding
    sub_class_obj = MySubClass1()
    assert (sub_class_obj.my_attr == 2)
    assert (sub_class_obj.config.scalar == 2)
    assert (sub_class_obj.config.string == 'my_string')
    assert (sub_class_obj.config.string2 == 'my_string2')